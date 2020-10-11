"""
主页接口序列化器
"""
from rest_framework import serializers
from apps.goods.models import GoodsVisitCount

# 定义一个序列还器，用于序列化GoodsVisitCount模型类数据
class GoodsVisitModelSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField() --> 序列化的结果是关联分类对象的主键值
    category = serializers.StringRelatedField()
    class Meta:
        model = GoodsVisitCount
        fields = ['category', 'count']