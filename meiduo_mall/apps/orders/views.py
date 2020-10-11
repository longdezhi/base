from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from django.db import transaction
from decimal import Decimal
from django_redis import get_redis_connection

from apps.users.models import Address
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from apps.goods.models import SKU
# Create your views here.


class OrderSettlementView(LoginRequiredJSONMixin, View):

    def get(self, request):
        user = request.user

        # 返回用户可选地址
        addresses = []
        add_queryset = Address.objects.filter(
            user=user,
            is_deleted=False
        )
        for address in add_queryset:
            addresses.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'receiver': address.receiver
            })

        # 返回选中的购物车数据
        skus = []

        conn = get_redis_connection('carts')
        # redis_skus = {b'1': b'5'}
        redis_skus = conn.hgetall('carts_%d'%user.id)
        # redis_selected = [b'1']
        redis_selected = conn.smembers('selected_%d'%user.id)

        for sku_id,count in redis_skus.items():
            # sku_id: b'1'; count: b'5'
            if sku_id in redis_selected:
                sku = SKU.objects.get(pk=int(sku_id))
                skus.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'count': int(count),
                    'price': sku.price
                })

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'context': {
                'addresses': addresses,
                'skus': skus,
                'freight': Decimal('10.5') # 计算的时候不会丢失精度
            }
        })


import json
from .models import *
from django.utils import timezone
# 保存/新建订单
class OrderCommitView(LoginRequiredJSONMixin, View):

    def post(self, request):

        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')

        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})

        try:
            Address.objects.get(pk=address_id)
        except Address.DoesNotExist as e:
            return JsonResponse({'code': 400, 'errmsg': '地址不存在'})

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': '付款方式不支持'})


        # 0、把购物车中的sku商品数据读取出来
        cart_dict = {} # {1: {"count": 5, "selected": True}}
        conn = get_redis_connection('carts')
        # {b"1": b"5"}
        redis_skus = conn.hgetall('carts_%d'%request.user.id)
        # [b'1']
        redis_selected = conn.smembers('selected_%d'%request.user.id)
        for sku_id,count in redis_skus.items():
            if sku_id in redis_selected:
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        sku_ids = cart_dict.keys()

        # 数据/业务处理
        # 1、新建订单表数据OrderInfo(主)
        # 20200912111256000001 ----> 约定订单的id的格式：时间戳 + 用户id(固定长度)
        # 加上时间戳可以保证这个订单的id唯一性
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%06d'%request.user.id
        freight = Decimal('10.5')


        with transaction.atomic():
            # 设置一个事务保存点
            save_id = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=request.user,
                address_id=address_id,
                total_count=0, # 初始化
                total_amount=0, # 初始化
                freight=freight,
                pay_method=pay_method
            )

            # 2、插入订单商品表数据OrderGoods(从) --> 具体的sku商品就是购物车中选中的商品
            for sku_id in sku_ids:

                # 乐观锁处理机制
                while True:
                    # 购物车中的sku商品
                    sku = SKU.objects.get(pk=sku_id)
                    # (1)、读旧的库存和销量
                    old_stock = sku.stock
                    old_sales = sku.sales
                    old_sales = sku.sales

                    # TODO: 判断库存和销量
                    # 用户下单量
                    count = cart_dict[sku_id]['count']
                    if count > old_stock:
                        # 库存不足, 回滚事务
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'code': 400, 'errmsg': '库存不足'}, status=400)

                    # 修改销量和库存数据
                    # sku.stock -= count
                    # sku.sales += count
                    # sku.save()

                    # (2)、基于旧库存和销量计算新值
                    new_stock = old_stock - count
                    new_sales = old_sales + count
                    # (3)、在旧库存和销量基础上，查询后修改
                    ret = SKU.objects.filter(
                        pk=sku.id,
                        stock=old_stock,
                        sales=old_sales
                    ).update(stock=new_stock, sales=new_sales)
                    # 如果update函数返回值为0，说明filter过滤结果为空，说明根据旧数据找不到原有的sku
                    # 说明有别的事务介入
                    if ret:
                        # 如果ret不为0，说明正确更新
                        break

                # 中间表OrderGoods表中插入一条数据，表示新建的订单中的sku商品
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=cart_dict[sku_id]['count'],
                    price=sku.price,
                )

                order.total_count += cart_dict[sku_id]['count']
                order.total_amount += cart_dict[sku_id]['count'] * sku.price

            order.total_amount += freight
            order.save()

            # 提交保存点（删除保存点）
            transaction.savepoint_commit(save_id)


        # 下单结束删除购物车
        conn.hdel('carts_%d'%request.user.id, *sku_ids)
        conn.srem('selected_%d'%request.user.id, *sku_ids)

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'order_id': order_id
        })


















