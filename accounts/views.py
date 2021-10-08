from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import UserForm


def register_view(request):
    form = UserForm(request.POST or None)
    context = {"form": form}
    if form.is_valid():
        user_obj = form.save()
        return redirect('/accounts/login/')
    else:
        context = {"form": form, "errors3": form.errors}
    
    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/upload/')
        else:
            context = {"form": form, "errors3": form.errors}
            return render(request, "accounts/login.html", context)
    else:
        form = AuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("/")
    return render(request, "accounts/logout.html")