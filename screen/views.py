from django.shortcuts import render
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse,JsonResponse,StreamingHttpResponse
import qrcode
from io import BytesIO
import base64
from PIL import Image
from random import uniform
import requests
from django.views.decorators.csrf import csrf_exempt
from .models import Hplc

def group_required(group_name):

    def in_group(user):
        return user.groups.filter(name=group_name).exists()

    return user_passes_test(in_group)

@login_required
@group_required('Super')
@csrf_exempt
def proxy_to_flask(request, path):
    flask_url = f"http://10.120.120.101:5050/{path}"
    
    try:
        response = requests.request(
            method=request.method,
            url=flask_url,
            headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
            data=request.body,
            stream=True,
            timeout=15
        )

        def stream_content():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return StreamingHttpResponse(
            stream_content(),
            status=response.status_code,
            content_type=response.headers.get('Content-Type'),
        )

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Cannot connect to Flask: {str(e)}", status=502)
    except Exception as e:
        return HttpResponse(f"Proxy error: {str(e)}", status=502)
    
@login_required
@group_required("Hplc")
def screen(request):
    return render(request,'screen/screen.html')

@login_required
@group_required("Lab Tech")
def fix(request):
    return render(request,"screen/fix.html")

@login_required
@group_required("Lab Tech")
def page(request,slug):

    if slug == "a":
        url = "http://10.0.0.192:5050/video_feed"
        try:
            response = requests.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
                data=request.body,
                stream=True,
                timeout=15
        )

            def stream_content():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            return StreamingHttpResponse(
                stream_content(),
                status=response.status_code,
                content_type=response.headers.get('Content-Type'),
            )

        except requests.exceptions.RequestException as e:
            return HttpResponse(f"Cannot connect to Flask: {str(e)}", status=502)
        except Exception as e:
            return HttpResponse(f"Proxy error: {str(e)}", status=502)


@login_required
@group_required("Lab Tech")
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
@group_required("Lab Tech")
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

@login_required
@group_required("Super")    
def app(request):
    return render(request,"screen/index.html")


    
@login_required
@group_required("Hplc")
def search(request):
    if request.method == "GET":
        name = request.GET.get('q')
        if name:
            hplc_db = Hplc.objects.filter(name__icontains=name)
            return render(request,"screen/search.html",{
                "hplc":hplc_db
            }) 
        
        else:
            hplc_db = Hplc.objects.all()
            return render(request,"screen/search.html",{
            "hplc":hplc_db
    })
            
    else:
        hplc_db = Hplc.objects.all()
        return render(request,"screen/search.html",{
        "hplc":hplc_db
    })