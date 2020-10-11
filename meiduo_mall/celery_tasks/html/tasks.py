
import os
from django.template import loader
from django.conf import settings
from apps.goods.utils import get_categories,get_goods_and_spec
from celery_tasks.main import celery_app

@celery_app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):

    """
    功能：生成指定sku商品的详情页面
    sku_id: SKU商品的id
    :return: 无
    """

    categories = get_categories()
    goods, sku, specs = get_goods_and_spec(sku_id)

    # =========模版渲染========
    template = loader.get_template('detail.html')
    context = {
        'categories': categories,
        'goods': goods,  # 当前sku从属的spu
        'specs': specs,  # 规格和选项信息
        'sku': sku  # 当前sku商品对象
    }
    page = template.render(context)

    # settings.STATIC_FILE_PATH --> 是front_end_pc文件夹路径
    file_path = os.path.join(
        settings.STATIC_FILE_PATH,
        'goods/%d.html' % sku_id, # 'goods/1.html'
    )

    with open(file_path, 'w') as f:
        f.write(page)