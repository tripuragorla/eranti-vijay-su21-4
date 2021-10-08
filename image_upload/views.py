from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ImageUploadForm
from .models import UploadedImage

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
        context['object'] = obj
        
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
            context['object'] = obj
            context['form'] = ImageUploadForm()
            return render(request, "image_upload/upload_page.html", context)
        else:
            context.update({"form": form, "errors": form.errors})
            return render(request, "image_upload/upload_page.html", context)
    else:
        form = ImageUploadForm()
    context["form"] = form
    return render(request, "image_upload/upload_page.html", context)

"""
@login_required
def process_image(request):
    object = UploadedImage.objects.get(user=request.user)
    image = object.image
    # process image for deep learning
"""