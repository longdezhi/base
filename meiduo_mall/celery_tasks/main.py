"""
main.py模块，作为异步服务的主脚本；
该文件中，定义异步应用对象
"""
import os

# 在celery异步程序的主脚本文件main.py中设置我们使用的django配置文件导包路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

from celery import Celery

# 1、初始化一个异步应用程序对象
celery_app = Celery('meiduo')

# 2、加载配置文件
celery_app.config_from_object('celery_tasks.config')

# 3、定义好任务之后，需要在异步任务应用对象中注册该任务
celery_app.autodiscover_tasks([
    'celery_tasks.sms', # 异步任务包的导包路径
    'celery_tasks.email',
])