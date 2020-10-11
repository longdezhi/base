
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from apps.users.models import User

class AdminGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name'
        ]

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'mobile',

            'password',
            'groups',
            'user_permissions'
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }


    def validate(self, attrs):
        raw_password = attrs.get('password')
        secret_password = make_password(raw_password)
        attrs['password'] = secret_password
        attrs['is_staff'] = True
        return attrs
