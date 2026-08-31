from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('/About',views.About,name="About"),
    path('/Disclaimer',views.Disclaimer,name='Disclaimer'),
    path('msg',views.msg,name='msg'),
    path("exp",views.lab_exp,name="exp"),
    path("lab",views.lab,name="lab"),
    path("illuminati", views.illuminati, name="illuminati"),
    path("username/", views.zelle_username, name="zelle_username"),
]
