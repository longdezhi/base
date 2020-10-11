
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from apps.users.models import User

class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'mobile',
            'email',

            'password'
        ]

        extra_kwargs = {
            'pasword': {'write_only': True, 'min_length': 8, 'max_length': 20, 'required': True},
            'username': {'max_length': 20, 'required': True},
            'mobile': {'required': True}
        }

    def validate(self, attrs):
        # 1、密码加密
        raw_password = attrs.pop('password') # 明文
        secret_password = make_password(raw_password) # make_password传入明文密码，加密返回密文码
        attrs['password'] = secret_password
        # 2、返回有效数据中添加is_staff=True
        attrs['is_staff'] = True

        return attrs

    # 模型类序列化器默认提供的create方法，无法实现密码加密和is_staff=True
    # def create(self, validated_data):
    #     # return User.objects.create_superuser(**validated_data) is_superuser=True and is_staff=True
    #     validated_data['is_staff'] = True # 员工
    #     return User.objects.create_user(**validated_data) # 密码加密







