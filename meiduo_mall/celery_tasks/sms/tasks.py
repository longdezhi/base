"""
该模块固定名称tasks.py
"""

from celery_tasks.main import celery_app
from celery_tasks.yuntongxun.ccp_sms import CCP

# 定义一个异步任务函数: 被celery_app.task装饰器装饰的函数就可以被异步调用！
@celery_app.task(name="ccp_send_sms_code")
def ccp_send_sms_code(mobile, sms_code):
    """
    功能：发送短信
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 可有可无
    """

    result = CCP().send_template_sms(
        mobile,
        [sms_code, 5],
        1
    )

    return result