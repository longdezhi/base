"""
封装加密和解密openid的接口
"""

from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings

# 原则上一个类的封装分为2个部分：
# 1、操作所需要的属性
# 2、函数方法

class SecretOauth(object):

    def __init__(self):
        # 由于加密和解密都需要TimedJSONWebSignatureSerializer对象
        # 就可以把该对象封装到属性中
        self.serializer = TimedJSONWebSignatureSerializer(
            secret_key=settings.SECRET_KEY, # 使用Django工程初始化的密钥
            expires_in=24 * 15 * 60
        )


    # (1)、加密
    def dumps(self, content_dict):
        """
        功能：加密openid
        参数：content_dict = {"open_id": "fnhewrbfhreubvw"}
        :return: 返回加密后的access_token
        """
        access_token = self.serializer.dumps(content_dict)
        return access_token.decode() # 返回的是一个字符串


    # (2)、解密
    def loads(self, access_token):
        """
        功能：解密access_token
        参数：access_token = "fewbfherbgerg.regwertgt.wgtrwgtfgrew"
        :return: 解密后的字典
        """
        try:
            data = self.serializer.loads(access_token)
        except Exception as e:
            # 解密/校验失败 —— 要么伪造了要么过了有效期
            return None

        # 校验成功返回解密后的字典{"openid": "fnhewrbfhreubvw"}
        return data