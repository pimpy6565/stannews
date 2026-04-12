from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse


# Create your views here.
@login_required
def screen(request):
    return render(request,'screen/screen.html')

@login_required
def fix(request):
    return render(request,"screen/fix.html")

def page(request,slug):

    if slug == "a":
        url = "http://10.120.120.101:5050/video_feed"
    if slug == "b":
        url = "http://10.120.120.249:5050/video_feed"
    else: 
        url = ""
    return render(request,"screen/page.html",{
        'urlstream':url
    })