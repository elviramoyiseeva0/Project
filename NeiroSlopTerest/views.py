from django.shortcuts import render
from django.http import HttpResponse
# from ..users.forms import RegisterForm, LoginForm

def index(request):
    return HttpResponse("NeiroSlopTerest")
