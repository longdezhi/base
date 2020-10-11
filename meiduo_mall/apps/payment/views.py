from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings

from alipay import AliPay

import os

from apps.orders.models import OrderInfo
from .models import Payment
# Create your views here.


# 支付接口1：扫码支付页面url获取
class PaymentView(View):
    def get(self, request, order_id):
        # 1、提取参数
        # 2、校验参数
        # 3、业务处理 —— 调用支付宝sdk获取扫码支付url
        # (1)、构建alipay支付对象
        alipay = AliPay(
            settings.ALIPAY_APPID, # 支付应用id
            app_notify_url=None, # 支付成功之后，支付宝回调地址
            app_private_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/app_private_key.pem'
            ),
            alipay_public_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/alipay_public_key.pem'
            ),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG

        )
        
        try:
            order = OrderInfo.objects.get(pk=order_id)
        except OrderInfo.DoesNotExist as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '订单不存在'})
        
        # (2)、找对象里面的方法获取支付参数
        # api_alipay_trade_page_pay：获取网页端支付页面url参数
        query_params = alipay.api_alipay_trade_page_pay(
            subject='美多商城支付%s' % order_id,
            out_trade_no=order_id,
            total_amount=float(order.total_amount),
            return_url=settings.ALIPAY_RETURN_URL, # 用户支付成功，请求美多的页面
        )


        # 扫码支付要么链接是：'https://openapi.alipaydev.com/gateway.do?<支付参数>'
        # (3)、拼接支付扫码页面url
        alipay_url = settings.ALIPAY_URL + '?' + query_params

        # 4、构建响应
        return JsonResponse({'code':0 ,'errmsg': 'ok', 'alipay_url': alipay_url})

# 接口二：支付成功，订单号绑定
class PaymentStatusView(View):

    def put(self, request):
        alipay = AliPay(
            settings.ALIPAY_APPID,  # 支付应用id
            app_notify_url=None,  # 支付成功之后，支付宝回调地址
            app_private_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/app_private_key.pem'
            ),
            alipay_public_key_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'keys/alipay_public_key.pem'
            ),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG

        )

        # 1、校验支付宝参数
        data = request.GET # Django查询字符串参数，类型是QueryDict
        data = data.dict() # QueryDict  转化成  dict
        # 此处使用get是错误的，需要把sign参数从字典中pop出来，此前因无法支付宝维护，此处无法调试
        # sign = data.get('sign')
        sign = data.pop('sign') # 签名 --> 使用该签名参数校验支付数据的有效性

        if not alipay.verify(data, signature=sign):
            # 校验失败，参数有误
            return JsonResponse({'code': 400, 'errmsg': '支付有误'})

        out_trade_no = data.get('out_trade_no') # 接口1中传递的order_id
        trade_no = data.get('trade_no') # 支付宝订单流水号

        try:
            Payment.objects.create(
                order_id=out_trade_no, # 美多订单号
                trade_id=trade_no # 支付宝订单流水号
            )
        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'errmsg': '新建支付订单失败'})

        order = OrderInfo.objects.get(pk=out_trade_no)
        order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        order.save()


        # 2、绑定美多商城订单
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'trade_id': trade_no})


















