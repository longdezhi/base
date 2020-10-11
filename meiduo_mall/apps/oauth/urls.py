

from django.urls import re_path
from . import views

urlpatterns = [
    # qq登陆接口1
    re_path(r'^qq/authorization/$', views.QQURLView.as_view()),
    # qq登陆接口2
    re_path(r'^oauth_callback/$', views.QQUserView.as_view()),
]