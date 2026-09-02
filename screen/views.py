from django.shortcuts import render, redirect
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse,JsonResponse,StreamingHttpResponse
import qrcode
from io import BytesIO
import base64
from PIL import Image
from random import uniform
import os
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from .models import Hplc, ThrowBatch, ShiftPost

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

LINE_FLASK = {
    1: os.environ.get("LINE1_FLASK_URL", "http://10.120.120.101:5050").rstrip("/"),
    2: os.environ.get("LINE2_FLASK_URL", "http://10.120.120.249:5050").rstrip("/"),
}


def _flask_base(n):
    return LINE_FLASK.get(int(n))


@login_required
@group_required("Lab Tech")
def line_mirror(request, n):
    if _flask_base(n) is None:
        return HttpResponse("Unknown line", status=404)
    return render(request, "screen/line_mirror.html", {"n": int(n)})


def _one_jpeg(url):
    r = requests.get(url, stream=True, timeout=12)
    r.raise_for_status()
    buf = b""
    for chunk in r.iter_content(chunk_size=4096):
        if not chunk:
            continue
        buf += chunk
        start = buf.find(b"\xff\xd8")
        end = buf.find(b"\xff\xd9")
        if start != -1 and end != -1 and end > start:
            r.close()
            return buf[start:end + 2]
        if len(buf) > 2_000_000:
            break
    r.close()
    return None


@login_required
@group_required("Lab Tech")
def line_snap(request, n):
    base = _flask_base(n)
    if not base:
        return HttpResponse("Unknown line", status=404)
    try:
        jpeg = _one_jpeg(f"{base}/video_feed")
        if not jpeg:
            return HttpResponse("No frame", status=502)
        return HttpResponse(jpeg, content_type="image/jpeg")
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Line PC unreachable: {e}", status=502)


@login_required
@group_required("Lab Tech")
def line_video(request, n):
    base = _flask_base(n)
    if not base:
        return HttpResponse("Unknown line", status=404)
    try:
        response = requests.get(f"{base}/video_feed", stream=True, timeout=(5, 60))

        def stream_content():
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            finally:
                response.close()

        return StreamingHttpResponse(
            stream_content(),
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "multipart/x-mixed-replace; boundary=frame"),
        )
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Line PC unreachable: {e}", status=502)


@login_required
@group_required("Lab Tech")
@csrf_exempt
def line_click(request, n):
    base = _flask_base(n)
    if not base:
        return JsonResponse({"error": "Unknown line"}, status=404)
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        r = requests.post(
            f"{base}/click",
            headers={"Content-Type": "application/json"},
            data=request.body,
            timeout=8,
        )
        try:
            payload = r.json()
        except Exception:
            payload = {"status": r.text}
        return JsonResponse(payload, status=r.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Line PC unreachable: {e}"}, status=502)


@login_required
@group_required("Lab Tech")
@csrf_exempt
def line_type(request, n):
    base = _flask_base(n)
    if not base:
        return JsonResponse({"error": "Unknown line"}, status=404)
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        r = requests.post(
            f"{base}/type",
            headers={"Content-Type": "application/json"},
            data=request.body,
            timeout=8,
        )
        try:
            payload = r.json()
        except Exception:
            payload = {"status": r.text}
        return JsonResponse(payload, status=r.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Line PC unreachable: {e}"}, status=502)

@login_required
@group_required("Hplc")
def screen(request):
    return render(request,'screen/screen.html')

@login_required
@group_required("Hplc")
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

@login_required
@group_required("Lab Tech")
def throw_calc(request):
    error = None
    if request.method == "POST":
        flavor = (request.POST.get("flavor") or "").strip()
        try:
            finished_brix = float(request.POST.get("finished_brix") or 0)
            syrup_brix = float(request.POST.get("syrup_brix") or 0)
            batch_gallons = float(request.POST.get("batch_gallons") or 0)
        except (TypeError, ValueError):
            error = "Numbers only."
            finished_brix = syrup_brix = batch_gallons = 0
        if error is None:
            if not flavor:
                error = "Flavor is required to save a batch."
            elif syrup_brix <= 0 or finished_brix <= 0:
                error = "Brix has to be greater than 0."
            elif finished_brix > syrup_brix:
                error = "Finished brix can't be higher than syrup brix."
            elif batch_gallons < 0:
                error = "Batch gallons can't be negative."
            else:
                syrup_gallons = batch_gallons * (finished_brix / syrup_brix)
                water_gallons = batch_gallons - syrup_gallons
                ThrowBatch.objects.create(
                    flavor=flavor[:80],
                    finished_brix=round(finished_brix, 3),
                    syrup_brix=round(syrup_brix, 3),
                    batch_gallons=round(batch_gallons, 3),
                    syrup_gallons=round(syrup_gallons, 3),
                    water_gallons=round(water_gallons, 3),
                    ran_by=request.user.username,
                )
                return redirect("throw")
    logs = ThrowBatch.objects.order_by("-created_at")[:25]
    return render(request, "screen/throw.html", {"logs": logs, "error": error})



@login_required
@group_required("Lab Tech")
def shift_log(request):
    error = None
    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if not body:
            error = "Type something."
        elif len(body) > 280:
            error = "Keep it to 280 characters."
        else:
            ShiftPost.objects.create(body=body[:280], posted_by=request.user.username)
            return redirect("shiftlog")
    posts = ShiftPost.objects.order_by("-created_at")[:80]
    return render(request, "screen/shiftlog.html", {"posts": posts, "error": error})


@login_required
@group_required("Lab Tech")
def shift_log_feed(request):
    from django.utils.dateformat import format as dateformat
    posts = ShiftPost.objects.order_by("-created_at")[:80]
    return JsonResponse({
        "posts": [
            {
                "id": p.id,
                "body": p.body,
                "posted_by": p.posted_by,
                "created_at": dateformat(p.created_at, "n/j g:i A"),
                "initial": (p.posted_by or "?")[:1].upper(),
            }
            for p in posts
        ]
    })

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
