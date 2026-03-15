from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import chats
# Create your views here.

def index(request):
    return render(request,'news/index.html')

def About(request):
    return render(request,'news/contact.html')

def Disclaimer(request):
    return render(request,'news/Disclaimer.html')

def msg(request):
    if request.method == "POST":
        message = request.POST.get('msg')
        New_msg = chats(text = message)
        New_msg.save()
        return JsonResponse({"msg": message})
    if request.method == "GET":
        messages = chats.objects.all().values("text")
        return JsonResponse({"msg": list(messages)})