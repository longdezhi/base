from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,JsonResponse
from verifications.libs.captcha.captcha import captcha
from verifications.libs.yuntongxun.ccp_sms import CCP
from django_redis import get_redis_connection
import re
import random

from celery_tasks.sms.tasks import ccp_send_sms_code
# Create your views here.

# 获取图片验证码
class ImageCodeView(View):

    def get(self, request, uuid):
        # 1、提取参数
        # 2、验证参数
        # 3、数据处理 —— 调用captcha包生成图片验证码，返回图片，并在redis中记录验证码
        # 3.1、使用captcha包获取图片和验证码
        text, image = captcha.generate_captcha()
        # 3.2、把验证码text记录到redis中，key是uuid

        try:
            conn = get_redis_connection('verify_code')
            conn.setex(
                'img_%s'%uuid, # img_fhjeiuw-fewfer-frewfrg
                300, # 300秒有效期
                text # "ABCD"
            )
        except Exception as e:
            print(e)
            return HttpResponse("", status=500)

        # 4、构建响应
        return HttpResponse(
            image, # 图片的字节数据
            content_type='image/jpeg' #
        )


# 发送短信验证码
class SMSCodeView(View):

    def get(self, request, mobile):
        # 1、提取参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2、校验参数
        # 2.1、参数必要性校验
        if not all([image_code, uuid]):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数缺失'
            }, status=400)

        # 2.2、校验image_code
        if not re.match(r'^[a-zA-Z0-9]{4}$', image_code):
            return JsonResponse({
                'code': 400,
                'errmsg': '图形验证码格式有误！'
            }, status=400)

        # 2.3、校验图片验证码的uuid
        if not re.match(r'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$', uuid):
            return JsonResponse({
                'code': 400,
                'errmsg': 'uuid不符合格式'
            }, status=400)

        # 2.4、校验用户输入的图形验证码和redis中记录的是否一致
        # 2.4.1、根据uuid提取redis中的图形验证码
        conn = get_redis_connection('verify_code')

        # 过期：None；
        # 存在：b'ABCD' ---> 'ABCD'
        image_code_from_redis = conn.get('img_%s'%uuid)
        # 图片验证码：读一次，删一次，保证该图片验证码只会被使用"一次"！
        conn.delete('img_%s'%uuid)
        if not image_code_from_redis:
            # 没有读取到redis中的图形验证码 —— 可能过期了
            return JsonResponse({
                'code': 400,
                'errmsg': '图形验证码过期！'
            }, status=403)

        # 读取到了redis的验证码是字符串的字节形式，需要转化成字符串
        image_code_from_redis = image_code_from_redis.decode()

        # 2.4.2、和用户手写的比对
        #  'ABCE' != 'ABCD'
        if image_code.lower() != image_code_from_redis.lower(): # 全部转为小写比较，目的是忽略大小写
            return JsonResponse({
                'code': 400,
                'errmsg': '验证码输入有误'
            }, status=400)


        # 3、数据处理 —— 发送手机短信
        # 3.0、判断redis的短信标志存不存在 —— 存在说明60秒之内用户发送过短信
        send_flag = conn.get('send_flag_%s' % mobile)
        if send_flag:
            return JsonResponse({'code': 400, 'errmsg': '请勿重复发送'}, status=403)

        # 3.1、生成6位短信验证码
        sms_code = "%06d" % random.randint(0, 999999)
        print("短信验证码: ", sms_code)

        # 3.2、短信验证码存入redis缓存
        # 3.2.1、通过redis链接对象获取一个管道
        pl = conn.pipeline()

        # 短信验证码存入redis中，便于用户注册的时候读取比对
        # 以手机号码，作为存入短信验证码的redis中key
        # 通过pl管道对象，调用的函数(执行指令)，此处并没有真正的执行，而是暂存
        pl.setex(
            'sms_%s' % mobile,
            300,
            sms_code
        )
        # conn.setex(
        #     'sms_%s' % mobile,
        #     300,
        #     sms_code
        # )
        # 3.3、存入一个标志 —— 表示用户在60秒内发送了短信
        pl.setex(
            'send_flag_%s' % mobile,
            60,
            '1'
        )
        # conn.setex(
        #     'send_flag_%s' % mobile,
        #     60,
        #     '1'
        # )

        # 批量执行管道中暂存的指令
        pl.execute()

        # 3.4、调用容联云接口发送短信
        # 发送短信验证码
        # CCP().send_template_sms(
        #     mobile,
        #     [sms_code, 5],
        #     1
        # )
        # 使用异步方式调用 —— django视图函数中发布任务
        ccp_send_sms_code.delay(mobile, sms_code)


        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok'
        })



























