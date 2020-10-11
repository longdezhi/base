"""
自定义用户传统身份认证的认证后端
目的：实现用户名或手机号，多账号登陆
"""

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q # Q将多个条件，构建成互为"或"的条件
from django.conf import settings
from django.utils import timezone
from .models import User
from meiduo_mall.utils.secret import SecretOauth


# 继承Django默认的传统认证后端
class UsernameMobileAuthBackend(ModelBackend):

    # 重写authenticate方法
    # 原因：默认的authenticate方法，只会根据username字段去过滤查找用户
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 允许多账号登陆的情况下，前端传来的"username"有可能是用户名也有可能是手机号

        try:
            # 1、先按用户名查找
            user = User.objects.get(
                # username=="18588269037" or mobile=="18588269037"
                Q(username=username) |  Q(mobile=username) | Q(email=username)
            )
        except User.DoesNotExist as e:
            return None # 用户名找不到，返回None表示认证失败


        # TODO:判断是否为管理站点页面登陆，如果是需要进一步校验is_staff=True
        # 如果是商城页面登陆，request是一个请求对象
        # 如果是管理站点页面登陆，request是一个None
        if request is None and not user.is_staff:
            return None

        # 3、某一个找到了，再校验密码
        if user.check_password(password):
            user.last_login = timezone.localtime()
            user.save()
            return user




def generate_verify_email_url(request):
    """
    功能：生成验证的url
    :param request: 请求对象
    :return: 返回验证url
    """
    user = request.user

    token = SecretOauth().dumps({
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    })

    # verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
    verify_url = settings.EMAIL_VERIFY_URL + token

    return verify_url








