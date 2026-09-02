from django.urls import path,re_path
from . import views
from django.contrib.auth import views as auth_views
from news.views import GatedLoginView

from django.views.generic import TemplateView
urlpatterns = [
    path("",views.screen,name='screen'),
    path("login/", GatedLoginView.as_view(template_name="screen/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("fix/",views.fix,name="fix"),
    path("page/<str:slug>",views.page,name="page"),
    path("qr",views.qrcodes,name="qr"),
    path("fill",views.fill,name="fill"),
    path('rando',views.rando,name='rando'),
    path("app/",views.app,name="app"),
    
    path('search',views.search,name="search"),
    path('proxy/<path:path>', views.proxy_to_flask, name='proxy_to_flask'),
    path("line/<int:n>/", views.line_mirror, name="line_mirror"),
    path("line/<int:n>/video/", views.line_video, name="line_video"),
    path("line/<int:n>/snap/", views.line_snap, name="line_snap"),
    path("line/<int:n>/click/", views.line_click, name="line_click"),
    path("line/<int:n>/type/", views.line_type, name="line_type"),
    path("throw/", views.throw_calc, name="throw"),
    path("shiftlog/", views.shift_log, name="shiftlog"),
    path("shiftlog/feed/", views.shift_log_feed, name="shiftlog_feed"),

    # Catch-all for React (must be LAST)
    re_path(r'^.*$', TemplateView.as_view(template_name='screen/index.html')),

]
