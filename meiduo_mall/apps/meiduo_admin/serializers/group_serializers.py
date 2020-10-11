
from django.contrib.auth.models import Group,Permission
from rest_framework import serializers


class GroupPermSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id',
            'name'
        ]

class GroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name',

            # 假设模型类序列化器可以完成该字段的校验和新建中间表数据；
            'permissions'
        ]

    # 模型类序列化器的create方法，会帮助我们根据ManyToManyField字段来构建中间表数据
    # 接下来手动使用ManyToManyField字段来构建中间表数据
    # def create(self, validated_data):
    #     permissions = validated_data.pop('permissions')
    #     # 1、新建主表分组对象
    #     group = Group.objects.create(**validated_data)
    #     # 2、根据前端传来的permisssions列表数据新增中间表
    #     group.permissions.set(permissions)
    #     # group.permissions = permissions
    #
    #     return group










