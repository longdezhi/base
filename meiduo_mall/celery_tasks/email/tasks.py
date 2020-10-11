
from celery_tasks.main import celery_app
from django.conf import settings
from django.core.mail import send_mail

@celery_app.task(name='send_verify_email')
def send_verify_email(to_email, verify_url):
    """
    功能：发送邮件
    :param to_email: 目标邮箱
    :param verify_url: 验证url
    :return: 1成，0失败
    """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    return send_mail(
        subject,
        '',
        from_email=settings.EMAIL_FROM,
        recipient_list=[to_email],
        html_message=html_message
    )