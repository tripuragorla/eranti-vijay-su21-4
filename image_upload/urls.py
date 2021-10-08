from django.urls import path
from image_upload.views import main_view, upload_page, about


urlpatterns = [
    path('', main_view),
    path('upload/', upload_page, name='upload_page'),
    path('about/', about, name='about')
]