
from django.urls import re_path,path
from . import views

urlpatterns = [
    # 获取图片验证码
    # re_path(r'^image_codes/(?P<uuid>[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12})/$', views.ImageCodeView.as_view()),
    path('image_codes/<uuid:uuid>/', views.ImageCodeView.as_view()),

    # 获取短信验证码
    path('sms_codes/<mobile:mobile>/', views.SMSCodeView.as_view())
]