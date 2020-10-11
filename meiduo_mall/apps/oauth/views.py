from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import login

from QQLoginTool.QQtool import OAuthQQ

from meiduo_mall.settings.dev import logger
from meiduo_mall.utils.secret import SecretOauth
from .models import OAuthQQUser
from apps.users.models import User
# Create your views here.


class QQURLView(View):

    # qq登陆接口1：获取扫码页面url
    def get(self, request):
        # 1、提取参数
        next = request.GET.get("next") # 前端用户指定的qq登陆成功之后跳转回的美多页面
        # 2、校验参数
        # 3、数据/业务处理 —— 获取扫码页面url
        # 3.1、实例化qq认证对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            # redirect_uri是用户扫码验证之后，重定向回美多的url
            redirect_uri=settings.QQ_REDIRECT_URI,
            # state是用户完成整个登陆流程之后，跳转到的美多页面
            state=next
        )
        # 3.2、获取扫码登陆页面的url
        login_url = oauth.get_qq_url()

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'login_url': login_url
        })


import json
class QQUserView(View):

    # qq登陆接口3：把用户的美多账号 和 用户的qq身份(openid) 进行绑定
    def post(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        mobile = data.get('mobile')
        password = data.get('password')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        # 2、校验参数
        if not all([mobile, password, sms_code, access_token]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数缺失'
            }, status=400)

        # 手机号，密码，短信格式校验，略

        # {"openid": "fewfewgvetght"}
        token_dict = SecretOauth().loads(access_token)
        if token_dict is None:
            return JsonResponse({
                'code': 400,
                'errmsg': '无效的qq身份！'
            }, status=400)
        openid = token_dict.get('openid')

        # 3、数据/业务处理：绑定qq
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist as e:
            # 3.1、根据手机号查找用户，没找到则新建并绑定
            user = User.objects.create_user(
                username=mobile,
                mobile=mobile,
                password=password
            )
        else:
            # 3.2、根据手机号查找用户，找到则检查密码
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '密码错误！'}, status=400)

        # 绑定账号
        OAuthQQUser.objects.create(
            user=user,
            openid=openid
        )

        login(request, user)
        # 4、构建响应
        response =  JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie(
            'username',
            user.username,
            max_age=24*14*3600
        )

        # 合并购物车
        request.user = user
        return merge_cart_cookie_to_redis(request, response)


    # qq登陆接口2：验证code获取openid
    def get(self, request):
        # 1、提取参数
        # 此处的code，是用户扫码验证qq身份成功之后，qq给用户
        # 用户转而携带到美多后台来的
        code = request.GET.get('code')
        # 2、校验参数
        # 2.1、必要性校验
        if not code:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少参数'
            }, status=400)

        # 3、数据/业务处理：验证code获取openid
        # 3.1、实例化qq认证对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state='/'
        )

        try:
            # 3.2、调用接口获取access_token
            access_token = oauth.get_access_token(code)
            # 3.3、调用接口获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            # 表示验证用户code失败
            print(e)
            logger.error('qq登陆验证失败')
            return JsonResponse({
                'code': 400,
                'errmsg': 'qq身份验证失败'
            }, status=400)

        # 代码走到此处，表明，美多后台已经成功获取了用户的openid
        # 3.4、判读用户的"美多商城账号"和"openid"是否绑定
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist as e:
            # 3.4.1、用户没有绑定qq
            # 把openid加密返回给用户，由用户在页面中数据账号和密码，再进一步调用接口3来进行绑定操作
            access_token = SecretOauth().dumps({
                'openid': openid
            })
            return JsonResponse({
                'code': 400, # 根据接口约定，自定义返回的code为400表示未绑定，前端就会跳转到绑定页面
                'errmsg': 'ok',
                'access_token': access_token
            })

        else:
            # 3.4.2、用户绑定过qq
            login(request, oauth_user.user)
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok'
            })
            response.set_cookie(
                'username',
                oauth_user.user.username,
                max_age=24*3600*14
            )

            # 合并购物车
            request.user = oauth_user.user
            return merge_cart_cookie_to_redis(request, response)

















