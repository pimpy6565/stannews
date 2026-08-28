from django.urls import path,re_path
from . import views
from django.contrib.auth import views as auth_views

from django.views.generic import TemplateView
urlpatterns = [
    path("",views.screen,name='screen'),
    path("login/", auth_views.LoginView.as_view(template_name="screen/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("fix/",views.fix,name="fix"),
    path("page/<str:slug>",views.page,name="page"),
    path("qr",views.qrcodes,name="qr"),
    path("fill",views.fill,name="fill"),
    path("throw/",views.throw_calc,name="throw"),
    path('rando',views.rando,name='rando'),
    path("app/",views.app,name="app"),
    
    path('search',views.search,name="search"),
    path('proxy/<path:path>', views.proxy_to_flask, name='proxy_to_flask'),

    # Catch-all for React (must be LAST)
    re_path(r'^.*$', TemplateView.as_view(template_name='screen/index.html')),

]
