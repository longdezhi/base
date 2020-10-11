"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include,register_converter

from meiduo_mall.utils.converters import *
# 注册自定义的转换器
register_converter(UsernameConverter, 'username')
register_converter(MobileConverter, 'mobile')


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'', include('apps.users.urls')),
    re_path(r'', include('apps.verifications.urls')),
    re_path(r'', include('apps.oauth.urls')),
    re_path(r'', include('apps.areas.urls')),
    re_path(r'', include('apps.goods.urls')),
    re_path(r'', include('apps.carts.urls')),
    re_path(r'', include('apps.orders.urls')),
    re_path(r'', include('apps.payment.urls')),

    # 后台管理站点路由映射
    # 基于restful更改，后台管理站点业务接口统一前缀为：meiduo_admin/
    re_path(r'^meiduo_admin/', include('apps.meiduo_admin.urls')),
]