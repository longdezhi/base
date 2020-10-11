
from django.db import models
from meiduo_mall.utils.models import BaseModel


class OAuthQQUser(BaseModel):
    """
    功能：把qq用户 和 美多商城用户进行绑定
    """

    # user 是个外键, 关联对应的用户 —— 美多商城用户
    user = models.ForeignKey('users.User',  on_delete=models.CASCADE, verbose_name='用户')

    # qq 布的用户身份id —— 用户使用qq扫码登陆之后，qq官方颁发的用户身份id
    openid = models.CharField(max_length=64,  verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'