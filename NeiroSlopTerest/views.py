from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Pin
from .forms import PinForm
# from ..users.forms import RegisterForm, LoginForm

def index(request):
    if request.method == "POST":
        form = PinForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("index")

    form = PinForm()
    pins = Pin.objects.all()

    return render(request, "NeiroSlopTerest/index.html", {
        "form": form,
        "pins": pins
    })
