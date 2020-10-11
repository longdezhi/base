from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
# Paginator：分页器对象，使用该对象可以把一个查询集进行分页
from django.core.paginator import Paginator, EmptyPage
from .models import SKU
from .utils import get_breadcrumb
# Create your views here.


class ListView(View):

    def get(self, request, category_id):
        # category_id是三级商品分类的id
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理 —— 根据三级分类过滤出sku商品，再分页返回
        sort = request.GET.get('ordering')
        # skus是一个查询集
        skus = SKU.objects.filter(
            category_id=category_id,
            is_launched=True
        ).order_by(sort)

        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        # 根据page和page_size去分页
        # 分页流程：
        # （1）、构建一个分页器对象
        paginator = Paginator(skus, page_size)
        # （2）、获取指定页
        try:
            # cur_page是skus查询集的子集
            cur_page = paginator.page(page)
        except EmptyPage as e:
            print(e)
            return JsonResponse({
                'code': 400,
                'errmsg': '找不到指定页'
            })

        sku_list = []
        for sku in cur_page:
            # sku:当前页中的每一个SKU对象
            sku_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'breadcrumb': get_breadcrumb(category_id),
            'list': sku_list,
            'count': paginator.num_pages # 总页数
        })



# 热销商品
class HotGoodsView(View):

    def get(self, request, category_id):
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理 —— 根据销量降序排列返回
        skus = SKU.objects.filter(
            category_id=category_id,
            is_launched=True
        ).order_by('-sales')[0:3]

        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'hot_skus': hot_skus
        })



# sku商品搜索接口
# from haystack.views import SearchView
# class MySearchView(SearchView):
#     # 当前继承的SearchView是HayStack工具提供的
#     # 该视图已经实现了一个self.get视图函数，来完成搜索
#
#     def create_response(self):
#         # 重写目的：构建一个json数据返回
#
#         # 核心方法self.get_context() --> 和ES通信获取检索的结果
#         context = self.get_context()
#
#         # 检索词：context['query']
#         # 当前页对象：context['page']
#         # 分页器对象：context['paginator']
#         #
#         # object_list存放的是SearchResult对象
#         # SearchResult.object是SKU对象
#         # 当前页存放的搜索结果：context['page'].object_list
#         #
#         # 默认每页数量
#         # context['paginator'].per_page
#         # 总数
#         # context['paginator'].count
#
#         ret_list = []
#         # 遍历出每一个搜索的结果：SearchResult对象
#         for result in context['page'].object_list:
#             # result: SearchResult对象
#             sku = result.object
#             ret_list.append({
#                 'id': sku.id,
#                 'name': sku.name,
#                 'price': sku.price,
#                 'default_image_url': sku.default_image.url,
#                 'searchkey': context['query'],
#                 'page_size': context['paginator'].per_page,
#                 'count': context['paginator'].count
#             })
#
#         # JsonResponse默认只能传入字典
#         # 如果传入的是列表，需要把safe设置为False
#         return JsonResponse(ret_list, safe=False)
































