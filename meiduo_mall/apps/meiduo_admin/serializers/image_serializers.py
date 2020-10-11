

from rest_framework import serializers
from apps.goods.models import SKUImage,SKU
from fdfs_client.client import Fdfs_client

class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = [
            'id',
            'name'
        ]


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = [
            'id',
            'sku',
            'image'
        ]

    # def validate(self, attrs):
    #     # sku类型是PrimaryKeyRelatedField;反序列化前端传来主键值，经过类型校验之后成了对应的对象
    #     # image字段类型是ImageField；发序列化前端传来文件数据，经过类型校验之后成了文件对象
    #
    #     #规则1：SKUImage(sku=<SKU对象>, image=<文件对象>) ---> image赋值为一个文件对象的话，会触发文件存储后端来完成；
    #     #规则2：SKUImage(sku=<SKU对象>, image="图片标示，图片id") ---> image赋值为一个字符串，那么就不会触发文件存储后端，直接将该字符串存入mysql；
    #
    #     # 手动实现上传图片
    #     image_obj = attrs.get('image') # 图片文件对象
    #     # (1)、在校验过程中，手动从文件对象中读取图片数据，上传fdfs
    #     conn = Fdfs_client('./meiduo_mall/settings/client.conf')
    #     res = conn.upload_by_buffer(image_obj.read())
    #     if res is None:
    #         raise serializers.ValidationError("fdfs上传失败！")
    #     # (2)、再把fdfs返回的文件标示(文件id)作为有效数据中image字段的值
    #     attrs['image'] = res['Remote file_id']
    #     return attrs









