from django.shortcuts import render
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            return HttpResponse("reg successful")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponse("login successful")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})