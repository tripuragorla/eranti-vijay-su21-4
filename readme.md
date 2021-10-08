## runserver locally
python3 manage.py runserver

## get the uploaaded image
object = UploadedImage.objects.get(user=request.user)
image = object.image

## tech stacks
1) language - Python-3.8.10
2) web framework - Django-3.2.7
3) db - sqlite3
4) css framework - Boostrap4.1.3
5) font  - fontawesome5.6.1