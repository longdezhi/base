"""
users应用的子路由模块
"""

from django.urls import re_path,path
from . import views

# 路由表(即使子应用没有任何路径映射，这个表必须存在)
urlpatterns = [
    # 用户名是否重复
    # re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),

    # 手机号是否重复
    # re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view()),

    # 用户注册
    re_path(r'^register/$', views.RegisterView.as_view()),

    # 用户传统登陆
    re_path(r'^login/$', views.LoginView.as_view()),

    # 用户退出登陆
    re_path(r'^logout/$', views.LogoutView.as_view()),

    # 用户中心页
    re_path(r'^info/$', views.UserInfoView.as_view()),

    # 新增邮箱
    re_path(r'^emails/$', views.EmailView.as_view()),
    # 验证邮箱
    re_path(r'^emails/verification/$', views.VerifyEmailView.as_view()),

    # 新增收货地址
    re_path(r'^addresses/create/$', views.CreateAddressView.as_view()),
    # 展示用户地址
    re_path(r'^addresses/$', views.AddressView.as_view()),
    # 更新和删除地址
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    re_path(r'addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    # 设置地址标题
    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),

    # 修改密码
    re_path(r'^password/$', views.ChangePasswordView.as_view()),

    # 记录历史
    re_path(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
]