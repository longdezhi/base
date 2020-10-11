from django.db import models
from django.contrib.auth.models import AbstractUser
from meiduo_mall.utils.models import BaseModel
# Create your models here.



# 自定义用户模型类
# 注意：由于我们需要使用django的身份认证、状态保持等功能，所以我们必须继承Django的用户基类
class User(AbstractUser):

    # 补充手机号字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号", null=True)

    # 新增 email_active 字段
    # 用于记录邮箱是否激活, 默认为 False: 未激活
    email_active = models.BooleanField(default=False,
                                       verbose_name='邮箱验证状态')

    # Address模型类单一对象，表示当前用户的默认地址
    default_address = models.ForeignKey(
        'users.Address',
        on_delete=models.SET_NULL, # 当用户删除了他当前的默认地址，该用户的default_address自动设置为NULL
        null=True, # 设置允许为NULL
        verbose_name='默认地址',
        related_name='default_user'
    )

    class Meta:
        db_table = 'tb_users'


    # 在 str 魔法方法中, 返回用户名称
    def __str__(self):
        return self.username


# User.set_password() 设置密码
# User.check_password() 校验明文密码
# User.objects.create() 新建User对象，但是密码不会加密
# User.objects.create_user() 新建User对象，并且自动加密密码
# User.objects.create_superuser() 新建User对象，并且自动加密密码，并且是一个管理员is_staff=True


class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')

    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    # blank=True --> 空白字符    null=True --> None
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        # 设置默认 已更新时间降序
        ordering = ['-update_time']