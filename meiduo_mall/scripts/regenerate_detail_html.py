#! /usr/bin/env python3

import os,sys
from django.template import loader

# /Users/weiwei/Desktop/meiduo_mall_sz39/meiduo_mall/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 由于当前脚本依赖django环境，所以需要提前加载django环境
# 1、设置django环境变量指定配置文件路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')
# 2、手动加载Django环境
import django
django.setup()

from django.conf import settings
from apps.goods.utils import *

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


if __name__ == '__main__':
    from apps.goods.models import SKU
    skus = SKU.objects.filter(is_launched=True)

    for sku in skus:
        generate_static_sku_detail_html(sku.id)
