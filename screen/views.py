from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def screen(request):
    return render(request,'screen/screen.html')

@login_required
def fix(request):
    return render(request,"screen/fix.html")