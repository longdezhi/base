
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_jwt.utils import jwt_payload_handler,jwt_encode_handler

# 明确，定义一个序列化器对username和password这两个字段进行校验
# 校验的前端传参是：{"username": 'weiwei', 'password': 'xxxxxx'}
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=20,
        allow_blank=False,
        allow_null=False
    )
    password = serializers.CharField(
        required=True,
        max_length=20,
        min_length=8,
        allow_blank=False,
        allow_null=False
    )

    # 登陆校验用户名和密码 —— 自定义校验
    def validate(self, attrs):
        # attrs = {"username": 'weiwei', 'password': 'xxxxxx'}
        # 1、传统身份校验(校验用户和密码)
        user = authenticate(**attrs)
        if user is None:
            raise serializers.ValidationError("用户名或密码错误！")

        # 2、传统身份校验成功 —— 签发token(令牌) —— 把该token作为有效数据的一部分
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 3、返回有效数据
        return {
            'user': user,
            'token': token
        }













