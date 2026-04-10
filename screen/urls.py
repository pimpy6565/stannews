from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("",views.screen,name='screen'),
    path("login/", auth_views.LoginView.as_view(template_name="screen/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("fix/",views.fix,name="fix")
]