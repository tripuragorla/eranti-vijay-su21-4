import os
from django import forms
from image_upload.models import UploadedImage

class ImageUploadForm(forms.ModelForm):
    MAX_UPLOAD_SIZE = 1024 * 1024 * 5
    FORMATS = [".jpeg", ".jpg", ".gif", ".png"]

    class Meta:
        model = UploadedImage
        fields = ("image",)
        widgets = {"image": forms.FileInput()}
    
    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError(
                "Please select an image."
            )
        extension = os.path.splitext(image.name)[1]
        if extension.lower() not in self.FORMATS:
            raise forms.ValidationError(
                f"Image extension {extension} not allowed."
                "Please upload only jpeg, jpg, gif or png images."
            )
        if image.size >= self.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(
                "Logo image must be less than 5MB. "
                "Please scale down your image and try again."
            )
        return image