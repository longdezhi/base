"""
注意：该模块名search_indexes.py名称固定
"""

from haystack import indexes
from .models import SKU

# 明确：被检索的数据是SKU模型类数据，针对SKU模型类构建"索引模型类"

# 固定的索引类名：<Django模型类> + Index
class SKUIndex(indexes.SearchIndex, indexes.Indexable):

    # text是复合字段(该字段同时存储的是sku.name,sku.caption,sku.id)，该字段就是将来用于搜索的固定字段
    # use_template=True表示，将来使用模版来指定该字段关联的Django模型类对象的属性
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回的Django模型类，就是被检索的模型类
        return SKU

    def index_queryset(self, using=None):
        # 返回SKU的查询集，将来就是把这个查询集里面所有的sku商品数据写入es中等待被检索
        return self.get_model().objects.filter(is_launched=True)