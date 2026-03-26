from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import chats
# Create your views here.
from django.core.mail import send_mail

def send_sms(number, message):
    # For Metro/T-Mobile
    recipient = f"{number}@tmomail.net"
    send_mail(
        subject='stanNews message',  # SMS ignores this
        message=message,
        from_email='you@example.com',
        recipient_list=[recipient],
        fail_silently=False,
    )

# Usage
send_sms('5551234567', 'Hello! Your database just updated.')
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
        send_sms(8568130439,message)
        return JsonResponse({"msg": message})
    if request.method == "GET":
        messages = chats.objects.all().values("text")
        return JsonResponse({"msg": list(messages)})