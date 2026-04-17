from django.shortcuts import render
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse,JsonResponse
import qrcode
from io import BytesIO
import base64
from PIL import Image
from random import uniform
# Create your views here.
@login_required
def screen(request):
    return render(request,'screen/screen.html')

@login_required
def fix(request):
    return render(request,"screen/fix.html")

@login_required
def page(request,slug):

    if slug == "a":
        url = "http://10.120.120.101:5050/video_feed"
    elif slug == "b":
        url = "http://10.120.120.249:5050/video_feed"
    else: 
        url = ""
    return render(request,"screen/page.html",{
        'urlstream':url
    })
    
@login_required
def qrcodes(request):
    if request.method == "POST":
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )

        qr.add_data(request.POST.get('code'))
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Load your icon (can be .png, .jpg, or .ico)
        logo = Image.open(finders.find("screen/stan.ico")).convert("RGBA")

# Resize logo
        qr_w, qr_h = qr_img.size
        logo_size = qr_w // 4
        logo = logo.resize((logo_size, logo_size))

        # ---- MAKE IT ROUND ----
        mask = Image.new("L", (logo_size, logo_size), 0)

        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)

        logo = logo.convert("RGBA")

        # Apply circular mask
        rounded_logo = Image.new("RGBA", (logo_size, logo_size))
        rounded_logo.paste(logo, (0, 0), mask=mask)

        logo = rounded_logo
        # Center position
        pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)

        # Paste logo into QR
        qr_img.paste(logo, pos, mask=logo)

        # Convert to base64 (no file saving)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return JsonResponse({"code":qr_base64})
        
    return render(request,"screen/qr.html")

@login_required
def fill(request):
    return render(request,"screen/fill.html")

def rando(request):
    if request.method == "GET":
        num1 = request.GET.get('number1')
        num2 = request.GET.get('number2')
        valves = request.GET.get('valves')
        valves = int(valves)
        num1 = float(num1)
        num2 = float(num2)
        random_numbers = [round(uniform(num1,num2),2) for _ in range(valves)]
       
        
        
        return JsonResponse({"number":random_numbers})
    
