from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UploadedImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to='images', null=True, blank=True)
    uploaded_time = models.DateTimeField(auto_now_add=True)