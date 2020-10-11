"""
自定义Django存储后端，实现ImageField.url属性返回完整的图片链接
"""

# Storage是默认的Django的存储后端
from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers

class FastDFSStorage(Storage):

    def _open(self, name, mode='rb'):
        # 打开django本地文件
        pass

    def _save(self, name, image_obj, max_length=None):
        # 如果SKUImage(image=<文件对象>) --> 当前存储后端的_save方法，完成图片的保存动作
        # 此处我们需要把文件保存到fdfs(上传到fdfs)
        # name: 文件名称，同时也是保存到Django本地的文件名称 ---> 无需使用
        # image_obj: 传来的文件对象 --> 就是ImageField字段在新建或者更新的时候被赋值的文件对象

        conn = Fdfs_client('./meiduo_mall/settings/client.conf')
        res = conn.upload_by_buffer(image_obj.read())
        if res is None:
            raise serializers.ValidationError('上传fdfs失败！')
        file_id = res['Remote file_id']

        # 注意：_save方法返回值就是当前字段，存储在mysql中的文件id
        return file_id

    def exists(self, name):
        # 功能：判断上传的文件在Django本地是否重复
        # True：表示重复
        # Fales：表示不重复
        return False

    def url(self, name):
        """
        功能：返回值就是ImageField.url属性 ---> 构建完整的图片(文件)链接
        :param name: ImageField类型字段在mysql中存储的值 ---> 文件索引标识"group1/M00/00/02/CtM3BVrPB5CALKn6AADq-Afr0eE1672090"
        :return: 图片链接
        """

        # return "group1/M00/00/02/CtM3BVrPB5CALKn6AADq-Afr0eE1672090"
        # return name
        # return "http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrPB5CALKn6AADq-Afr0eE1672090"
        # return "http://image.meiduo.site:8888/" + name
        return settings.FDFS_BASE_URL + name