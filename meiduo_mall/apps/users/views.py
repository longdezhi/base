from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings


import json
import re
# login函数：把用户信息写入session缓存，并且设置cookie值
from django.contrib.auth import login,logout

# authenticate是一个全局的工具函数，功能：校验username和password
from django.contrib.auth import authenticate

from .models import User,Address
from meiduo_mall.settings.dev import logger
from meiduo_mall.utils.secret import SecretOauth
from .utils import generate_verify_email_url

from apps.carts.utils import merge_cart_cookie_to_redis
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_verify_email

from apps.goods.models import GoodsVisitCount
from django.utils import timezone
# Create your views here.


# 判断用户名重复接口
class UsernameCountView(View):

    def get(self, request, username):
        # 1、提取传参
        # 2、校验参数
        # 3、数据处理

        # 原则：一般针对数据库写操作进行异常捕获，而读操作根据需求自行决定；
        try:
            count = User.objects.filter(
                username=username
            ).count()
        except Exception as e:
            # 记录日志信息  和  构建一个响应
            logger.error('数据库错误！')
            return JsonResponse({
                'code': 400,
                'errmsg': '数据库错误'
            }, status=500)


        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count': count
        })


# 判断手机号重复接口
class MobileCountView(View):

    def get(self, request, mobile):
        # 1、提取参数
        # 2、校验参数
        # 3、数据处理
        try:
            count = User.objects.filter(
                mobile=mobile
            ).count()
        except Exception as e:
            logger.error('查询手机号重复，错误')
            return JsonResponse({
                'code': 400,
                'errmsg': '查询手机号重复，错误'
            }, status=500)


        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'count': count
        })


# 用户注册
class RegisterView(View):

    def post(self, request):
        # 1、提取参数
        # b'{"username": "xxx"...}' ---> '{"username": "xxx"...}'
        data = request.body.decode()
        # data = {"username": "xxx"...}是一个python字典
        data = json.loads(data)

        # 2、校验参数
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')

        allow = data.get('allow', False)

        # 2.1、必要性校验(是否必传)
        if not all([username, password, password2, mobile, sms_code]):
            # 参数缺失
            return JsonResponse({
                'code': 400,
                'errmsg': "参数缺失",
            }, status=400) # http响应状态码400表示请求参数有误
        # 2.2、单独字段校验
        if not allow:
            return JsonResponse({
                'code': 400,
                'errmsg': '请同意协议'
            })

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({
                'code': 400,
                'errmsg': '用户名格式有误！'
            })
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': 'password格式有误!'})
        if password != password2:
            return http.JsonResponse({'code': 400, 'errmsg': '两次输入不对!'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': 'mobile格式有误!'})

        # TODO:将来实现完短信验证码接口之后，此处需要填充验证短信验证码业务
        from django_redis import get_redis_connection
        conn = get_redis_connection('verify_code')
        sms_code_from_redis = conn.get('sms_%s'%mobile)
        if not sms_code_from_redis:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码过期'}, status=403)
        sms_code_from_redis = sms_code_from_redis.decode()
        if sms_code != sms_code_from_redis:
            return JsonResponse({'code': 400, 'errmsg': '输入的短信验证码有误'}, status=400)
        
        # 3、数据处理——新建用户
        try:    
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception as e:
            logger.error('用户新建，数据库写入失败')
            return JsonResponse({'code': 400, 'errmsg': '新建用户失败'}, status=500)


        # TODO:当用户注册成功，相当于用户登陆，我们需要记录用户信息 —— 状态保持
        # (1)、把用户数据写入session缓存——redis
        # (2)、在返回当时候，把sessionid设置在浏览器当Cookie中
        login(request, user)

        # 4、构建响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})

        # 5、再cookie中设置用户名，用作前端页面展示
        response.set_cookie(
            key='username',
            value=user.username,  # 固定页面展示用户名
            max_age=3600 * 24 * 14
        )

        # 合并购物车
        requset.user = user
        return merge_cart_cookie_to_redis(request, response)


# 用户登陆接口 —— 传统身份认证
class LoginView(View):

    def post(self, request):
        # 1、提取参数
        data = json.loads(
            request.body.decode()
        )
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered', False)

        # 2、校验参数
        # 2.1、必要性校验
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'}, status=400)
        # 2.2、字段校验
        if not re.match(r'^[a-zA-Z0-9_@.-]{5,20}$', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名格式有误'}, status=400)
        if not re.match(r'^\w{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '密码格式有误'}, status=400)

        # 3、数据/业务处理 —— 校验用户名和密码
        # 3.1、尝试着根据username获取用户对象
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            # 找不到用户，username写错误 或 没注册
            return JsonResponse({'code': 400, 'errmsg': '用户或密码输入有误'}, status=400)

        # 3.2、检查密码: User模型类对象继承自AbstractUser提供check_password函数用于校验明文密码
        if not user.check_password(password):
            # 密码错误
            return JsonResponse({'code': 400, 'errmsg': '用户或密码输入有误'}, status=400)
        """
        # 功能：验证用户名和密码 ---> 业务逻辑：通过用户名查找用户，再校验密码
        # 参数：request请求对象，username用户名，password明文密码
        # 返回值：用户名和密码校验成功返回用户对象，否则返回None
        # 全局函数authenticate ---调用--->  ModelBackend.authenticate实例方法完成用户名和密码校验
        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '用户或密码输入有误'}, status=400)

        # 状态保持
        login(request, user)

        # 设置session数据的有效期
        if remembered != True:
            # 用户没有勾选"记住用户" —— 有效期设置为0 —— 当用户关闭浏览器标签页则session失效
            request.session.set_expiry(0)
        else:
            # 用户勾选了"记住用户" —— 有效期设置为None —— 使用django默认的14天有效期
            request.session.set_expiry(None)

        # 4、构建响应
        response = JsonResponse({'code': 0, 'errmsg': "ok"})

        # 5、再cookie中设置用户名，用作前端页面展示
        response.set_cookie(
            key='username',
            value=user.username, # 固定页面展示用户名
            max_age=3600 * 24 * 14
        )

        # 合并购物车
        return merge_cart_cookie_to_redis(request, response)


# 用户退出登陆
class LogoutView(View):

    def delete(self, request):
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理
        # 通过request--->获取cookie中的sessionid--->根据sessionid删除redis中的用户数据
        logout(request)
        # 4、构建响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response


# 获取用户中心页数据
# LoginRequiredMixin：如果一个类视图继承自LoginRequiredMixin，那么这个类视图中所有的接口必须登陆才能访问
class UserInfoView(LoginRequiredJSONMixin, View):

    def get(self, request):
        # 1、验证用户是否登陆
        # request.user:
        # 1、如果用户已经登陆(cookie中有sessionid)，
        # 在请求的时候后端会根据sessionid查找用户数据，并且把request.user设置为查找到的用户模型类对象
        # 一句话：request.user就是当前已经登陆的用户对象
        # 2、如果用户未登陆，则request.user是一个AnonymousUser对象——匿名用户对象

        # 如果已经登陆：request.user.is_authenticated == True
        # 如果未登陆： request.user.is_authenticated == False
        # if not request.user.is_authenticated:
            # 未登陆
            # return JsonResponse({'code': 0, 'errmsg': '未登陆！'}, status=401)


        # 2、获取用户对象，构造响应参数
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'info_data': {
                'username': request.user.username,
                'mobile': request.user.mobile,
                'email': request.user.email,
                'email_active': request.user.email_active
            }
        })


# 新增用户邮箱
class EmailView(LoginRequiredJSONMixin, View):

    def put(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        email = data.get('email')
        # 2、校验参数
        if not email:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少参数'
            }, status=400)

        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            return JsonResponse({
                'code': 400,
                'errmsg': '邮箱格式有误'
            }, status=400)

        # 邮箱是否被注册
        count = User.objects.filter(email=email).count()
        if count:
            return JsonResponse({
                'code': 400,
                'errmsg': '该邮箱已被注册'
            }, status=400)

        try:
            # 3、数据/业务处理 —— 给当前登陆用户添加邮箱
            user = request.user # 依赖session机制
            user.email = email
            user.email_active = False
            user.save()
        except Exception as e:
            logger.error('修改邮箱，写入数据库失败')
            return JsonResponse({
                'code': 500,
                'errmsg': '修改邮箱，写入数据库失败'
            }, status=500)


        # TODO: 新增邮箱成功，发送验证邮件
        verify_url = generate_verify_email_url(request)
        # 发送邮件任务(函数)，使用异步方式调用
        # send_verify_email(email, verify_url) # 普通函数调用
        send_verify_email.delay(email, verify_url) # 异步函数调用

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


# 验证邮箱 —— 用户点击验证邮件链接发送的接口请求
class VerifyEmailView(View):

    def put(self, request):
        # 1、提取参数
        token = request.GET.get('token')
        # 2、校验参数
        if not token:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少token'
            })
        # 验证token是否有效
        # data= {"user_id": xx, "username": xx, "email":xx}
        data = SecretOauth().loads(token)
        if data is None:
            return JsonResponse({
                'code': 400,
                'errmsg': 'token无效'
            })

        # 3、数据/业务处理 —— 把邮箱的状态设置为True表示激活
        user_id = data.get('user_id')
        email = data.get('email')
        user = User.objects.get(pk=user_id, email=email)
        user.email_active = True
        user.save()

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


# 新增用户收件地址
class CreateAddressView(LoginRequiredJSONMixin, View):

    def post(self, request):
        # 1、提取参数
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2、校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({'code': 400, 'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({'code': 400, 'errmsg': '参数email有误'})

        try:
            # 3、数据处理 —— insert数据库插入/新建
            address = Address.objects.create(
                user=request.user,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,

                title=receiver, # 默认地址标题就是收件人名字
                receiver=receiver,
                place=place,
                mobile=mobile,
                tel= tel,
                email=email
            )
            # 如果当前用户没有默认地址，则把当前新增地址设置为默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            print(e)
            logger.error('新增地址数据库写入失败')
            return JsonResponse({
                'code': 400,
                'errmsg': '新增地址数据库写入失败'
            }, status=500)


        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
        })





# 用户地址展示
class AddressView(LoginRequiredJSONMixin, View):

    def get(self, request):
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理 —— 根据当前登陆用户，查找所有地址
        user = request.user
        # addresses = user.addresses.all()
        addresses = Address.objects.filter(user=user, is_deleted=False)

        address_list = []
        for address in addresses:
            address_dict = {
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email
            }

            # 当且精当用户默认地址存在，才需要去判断是否展示的是默认地址加入头部
            if user.default_address and address.id == user.default_address.id:
                # 当前地址是用户的默认地址
                address_list.insert(
                    0,
                    address_dict
                )
            else:
                # address是Address模型类对象
                address_list.append(address_dict)

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'default_address_id': user.default_address_id,
            'addresses': address_list
        })


class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):

    # 更新用户地址
    def put(self, request, address_id):

        # 1、提取参数
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2、校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.JsonResponse({'code': 400, 'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.JsonResponse({'code': 400, 'errmsg': '参数email有误'})

        try:
            # 3、数据/业务处理 —— update更新地址数据
            json_dict.pop('province')
            json_dict.pop('city')
            json_dict.pop('district')

            Address.objects.filter(
                pk=address_id
            ).update(**json_dict) # update(receiver="韦小宝")
        except Exception as e:
            print(e)
            logger.error('修改地址错误')
            return JsonResponse({'code': 500, 'errmsg': '修改地址写入失败'})

        address = Address.objects.get(pk=address_id)
        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'address': {
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email
            }
        })

    # 逻辑删除单一用户地址
    def delete(self, request, address_id):
        address = Address.objects.get(pk=address_id)
        address.is_deleted = True
        address.save()

        user = request.user
        if user.default_address_id == address.id:
            user.default_address = None
            user.save()

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })



# 用户设置默认地址
class DefaultAddressView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        # 当前登陆用户，把默认地址设置为address_id地址
        address = Address.objects.get(pk=address_id)
        user = request.user

        # user.default_address_id = address_id
        user.default_address = address
        user.save()

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })


# 用户设置地址标题
class UpdateTitleAddressView(View):

    def put(self, request, address_id):
        data = json.loads(request.body.decode())
        title = data.get('title')

        address = Address.objects.get(pk=address_id)
        address.title = title
        address.save()

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })




# 修改用户密码
class ChangePasswordView(View):

    def put(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')

        # 2、校验参数
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})

        # 校验旧密码
        if not request.user.check_password(old_password):
            return JsonResponse({'code': 400, 'errmsg': '密码错误'})

        # 校验新密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.JsonResponse({'code': 400,
                                      'errmsg': '密码最少8位,最长20位'})
        # 新密码2次输入是否一直
        if new_password != new_password2:
            return JsonResponse({'code': 400, 'errmsg': '2次输入密码不匹配'})

        # 3、数据/业务处理 —— 修改密码
        request.user.set_password(new_password)
        request.user.save()

        # TODO：修改密码，需要清除登陆数据
        logout(request)
        # 4、构建响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response

from apps.goods.models import SKU
from django_redis import get_redis_connection
# 用户浏览历史记录
class UserBrowseHistory(LoginRequiredJSONMixin, View):

    # 添加历史
    def post(self, request):

        user = request.user
        # 1、提取参数
        # 2、校验参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        if not sku_id:
            return JsonResponse({
                'code': 400,
                'errmsg': '缺少参数'
            }, status=400)

        try:
            sku = SKU.objects.get(pk=sku_id, is_launched=True)
        except SKU.DoesNotExist as e:
            return JsonResponse({
                'code': 404,
                'errmsg': '商品已下架/不存在'
            }, status=404)

        # 3、数据/业务处理 —— 把访问的sku的id写入redis表示记录一条浏览历史
        # 3.1、获取"history"缓存配置的redis链接
        conn = get_redis_connection('history')
        p = conn.pipeline()
        # 3.2、历史记录写入缓存
        # 3.2.1、去重
        p.lrem(
            'history_%d' % user.id,
            0, # 删除所有指定成员
            sku_id
        )
        # 3.2.2、插入列表头
        p.lpush(
            'history_%d' % user.id,
            sku_id
        )
        # 3.2.3、截断保留5个记录
        p.ltrim(
            'history_%d' % user.id,
            0,
            4
        )
        p.execute() # 批量执行redis指令


        # TODO: 记录该sku商品的分类访问量
        # 分类id：sku.category_id
        # 当日零时刻：
        cur_0_time = timezone.localtime().replace(hour=0, minute=0, second=0)
        # (1)、判断当前sku商品的分类，和当日的数据存不存在；
        try:
            visit_obj = GoodsVisitCount.objects.get(
                category_id=sku.category_id,
                create_time__gte=cur_0_time
            )
        except GoodsVisitCount.DoesNotExist as e:
            # 记录不存在则新建
            GoodsVisitCount.objects.create(
                category_id=sku.category_id,
                count=1
            )
        else:
            # 记录存在则累加
            visit_obj.count += 1
            visit_obj.save()

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })

    # 查看历史
    def get(self, request):

        user = request.user
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理 —— 用户浏览的sku商品信息返回(读redis获取最近浏览的历史sku.id, 读mysql获取sku详细信息)
        # 3.1、读redis获取浏览历史
        conn = get_redis_connection('history')
        # sku_ids = [b'6', b'3', b'4', b'14', b'15']
        sku_ids = conn.lrange(
            'history_%d' % user.id,
            0,
            -1
        )

        skus = [] # 用于记录返回sku商品的详细信息
        # 3.2、读mysql获取详细信息
        for sku_id in sku_ids:
            # sku_id = b'6'
            sku = SKU.objects.get(pk=int(sku_id))
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'skus': skus
        })
















