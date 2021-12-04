import csv
import pickle
import sys
import warnings
from random import randint

import torch
from PIL import Image
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from torchvision import transforms

from inversecooking.args import get_parser
from inversecooking.model import get_model
from inversecooking.utils.output_utils import prepare_output
from .forms import ImageUploadForm
from .models import UploadedImage

print("Initializing nutritional facts...", end="")
nutritional_facts = {}
with open("SmartFoodie_NutritionalFacts.csv", "rt") as f:
    reader = csv.DictReader(f)
    for fact in reader:
        ingredient = fact["ingredient"].title()
        fact = {
            "ingredient": ingredient,
            "carb": float(fact["carb"]),
            "fat": float(fact["fat"]),
            "cal": float(fact["cal"])
        }
        nutritional_facts[ingredient] = fact
print("done!")

print("Initializing nutritional model...", end="")
warnings.filterwarnings("ignore")

use_gpu = True
device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
map_loc = None if torch.cuda.is_available() and use_gpu else "cpu"

ingrs_vocab = pickle.load(open("ingr_vocab.pkl", "rb"))
vocab = pickle.load(open("instr_vocab.pkl", "rb"))
ingr_vocab_size = len(ingrs_vocab)
instrs_vocab_size = len(vocab)
output_dim = instrs_vocab_size

sys.argv = [""]
del sys
args = get_parser()
args.maxseqlen = 15
args.ingrs_only = False

model = get_model(args, ingr_vocab_size, instrs_vocab_size)
model.load_state_dict(torch.load("modelbest.ckpt", map_location=map_loc))
model.to(device)
model.eval()
model.ingrs_only = False
model.recipe_only = False

transf_list_batch = [transforms.ToTensor(), transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))]
to_input_transf = transforms.Compose(transf_list_batch)

greedy = [True, False, False, False]
beam = [-1, -1, -1, -1]
temperature = 1.0
numgens = 1  # len(greedy)
print("done!")


def random(a: float, b: float):
    return randint(int(a), int(b)) + (randint(0, 9) / 10)


def retrieve(ingredient: str):
    ingredient = ingredient.replace("_", " ").title()
    fact = nutritional_facts.get(ingredient)
    if fact is None:
        lower = nutritional_facts["1Q"]
        upper = nutritional_facts["3Q"]
        fact = {
            "ingredient": ingredient,
            "carb": random(lower["carb"], upper["carb"]),
            "fat": random(lower["fat"], upper["fat"]),
            "cal": random(lower["cal"], upper["cal"])
        }
        nutritional_facts[ingredient] = fact
    return fact


def predict(path: str):
    print("Running prediction on " + path + "...", end="")
    preds = []

    image = Image.open(path).convert("RGB")

    transf_list = [transforms.Resize(256), transforms.CenterCrop(224)]
    transform = transforms.Compose(transf_list)

    image_transf = transform(image)
    image_tensor = to_input_transf(image_transf).unsqueeze(0).to(device)

    for i in range(numgens):
        with torch.no_grad():
            outputs = model.sample(image_tensor, greedy=greedy[i],
                                   temperature=temperature, beam=beam[i], true_ingrs=None)

        ingr_ids = outputs["ingr_ids"].cpu().numpy()
        recipe_ids = outputs["recipe_ids"].cpu().numpy()
        outs, valid = prepare_output(recipe_ids[0], ingr_ids[0], ingrs_vocab, vocab)

        ingredients = list(map(retrieve, outs["ingrs"]))

        total = {
            "carb": round(sum([i["carb"] for i in ingredients]), 2),
            "fat": round(sum([i["fat"] for i in ingredients]), 2),
            "cal": round(sum([i["cal"] for i in ingredients]), 2)
        }

        preds.append({
            "title": outs["title"].title(),
            "ingredients": ingredients,
            "total": total,
            "recipe": outs["recipe"],
            "is_valid": valid["is_valid"]
        })

    print("done!")
    print("Predictions: " + str(preds))
    return preds


def main_view(request):
    return render(request, "image_upload/home.html")


def about(request):
    return render(request, "image_upload/about.html")


@login_required
def upload_page(request):
    context = {}
    last_upload = UploadedImage.objects.filter(user=request.user)
    if last_upload:
        obj = last_upload.first()
        context["object"] = obj

    if request.method == "POST":
        form = ImageUploadForm(request, request.FILES)
        if form.is_valid():
            try:
                obj = UploadedImage.objects.get(user=request.user)
                obj.delete()
            except UploadedImage.DoesNotExist:
                pass
            finally:
                obj = form.save(commit=False)
                obj.user = request.user
                obj.save()
            context["object"] = obj
            context["form"] = ImageUploadForm()
            context["prediction"] = predict(obj.image.path)
            return render(request, "image_upload/upload_page.html", context)
        else:
            context.update({"form": form, "errors": form.errors})
            return render(request, "image_upload/upload_page.html", context)
    else:
        form = ImageUploadForm()
    context["form"] = form
    return render(request, "image_upload/upload_page.html", context)
