from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return render(request,'news/index.html')

def About(request):
    return render(request,'news/contact.html')

def Disclaimer(request):
    return render(request,'news/Disclaimer.html')