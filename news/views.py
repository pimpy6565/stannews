from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import chats
from django.core.mail import send_mail
import threading


def send_sms(number, message):
    """Send SMS via email-to-SMS gateway (T-Mobile)"""
    try:
        recipient = f"{number}@tmomail.net"
        send_mail(
            subject='stanNews message',  # SMS ignores this
            message=message,
            from_email=None,
            recipient_list=[recipient],
            fail_silently=True,          # don't crash if SMS fails
        )
    except:
        pass  # never let SMS problems break the chat


def send_sms_background(number, message):
    """Fire-and-forget SMS in background thread"""
    threading.Thread(
        target=send_sms,
        args=(number, message),
        daemon=True
    ).start()


@csrf_exempt
def msg(request):
    if request.method == "POST":
        message = request.POST.get('msg', '').strip()
        
        if message:
            # Save to database
            New_msg = chats(text=message)
            New_msg.save()
            
            # Send SMS WITHOUT slowing down the chat
            send_sms_background(8568130439, message)
            
            return JsonResponse({"status": "success", "msg": message})
        
        return JsonResponse({"status": "error", "msg": "Empty message"}, status=400)

    if request.method == "GET":
        # ONLY last 80 messages + newest first = way faster
        messages = chats.objects.all().order_by('-id')[:80].values("text")
        return JsonResponse({"msg": list(messages)})

    return JsonResponse({"msg": []})


def index(request):
    return render(request, 'news/index.html')


def About(request):
    return render(request, 'news/contact.html')


def Disclaimer(request):
    return render(request, 'news/Disclaimer.html')


def lab_exp(request):
    return render(request, "news/exp.html")


def lab(request):
    return render(request, "news/lab.html")


def illuminati(request):
    """Professional application page for the Pepsi QC Illuminati secret society."""
    if request.method == "POST":
        name = (request.POST.get('name') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        badge = (request.POST.get('badge') or '').strip()
        shift = (request.POST.get('shift') or '').strip()
        years = (request.POST.get('years') or '').strip()
        reason = (request.POST.get('reason') or '').strip()
        alias = (request.POST.get('alias') or 'Nameless Initiate').strip()

        if not name or not reason:
            return JsonResponse({"status": "error", "message": "Name and petition reason are required."}, status=400)

        sms = (
            "🧿 PEPSI QC ILLUMINATI — NEW PETITION RECEIVED\n"
            f"Initiate: {name}\n"
            f"Contact: {phone or 'REDACTED'}\n"
            f"Badge: {badge or '—'}\n"
            f"Shift: {shift or '—'}\n"
            f"Tenure: {years or '—'} yrs\n"
            f"Alias: {alias}\n\n"
            f"Petition:\n{reason}\n\n"
            "The Council has been notified. All eyes are watching."
        )
        send_sms_background(8568130439, sms)

        return JsonResponse({
            "status": "success",
            "message": "Your application has been received by the Inner Council. You will be contacted via secure channel when a decision is reached."
        })

    return render(request, 'news/illuminati.html')
