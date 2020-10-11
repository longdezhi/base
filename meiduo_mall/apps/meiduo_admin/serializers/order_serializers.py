
from rest_framework import serializers
from apps.orders.models import OrderInfo,OrderGoods
from apps.goods.models import SKU

class OrderSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = [
            'order_id',
            'create_time'
        ]

# ============单独定义一个用于订单详情的序列化器===========

class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = [
            'name',
            'default_image'
        ]

class OrderGoodsModelSerializer(serializers.ModelSerializer):
    # 当前订单商品对象关联的"单一的"SKU对象
    sku = SKUSimpleSerializer()

    class Meta:
        model = OrderGoods
        fields = [
            'count',
            'price',
            'sku'
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    # 当前订单对象关联的多个订单商品(OrderGoods)对象
    skus = OrderGoodsModelSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = "__all__"