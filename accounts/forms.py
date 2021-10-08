from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name','last_name', 'username', 'email', 'password1' ,'password2' )
    
    def clean_email(self):
        data = self.cleaned_data
        email = data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email id is already registered.")
        return email