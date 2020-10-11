from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache

from .models import Area
# Create your views here.


# 新建收货地址前置接口1：获取省级行政区信息
class ProvinceAreasView(View):

    def get(self, request):
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理：读取省数据

        # 通读策略步骤1：读缓存redis
        province_list = cache.get('province_list') # 缓存没有则返回None

        if not province_list:
            # 通读策略步骤2：读mysql
            provinces = Area.objects.filter(
                parent=None
                # parent__isnull=True # 等价parent=None
            )

            province_list = [] # province_list就是需要被缓存读数据
            for province in provinces:
                # province：Area对象(省对象)
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })

            # 通读策略步骤3：缓存回填
            cache.set('province_list', province_list, 3600)

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'province_list': province_list
        })


# 新建收货地址前置接口2：获取市、区信息
class SubAreasView(View):

    def get(self, request, pk):
        # 1、提取参数
        # 2、校验参数
        # 3、数据/业务处理：根据pk过滤出子级行政区信息返回

        # area是父级行政区
        area = Area.objects.get(pk=pk)

        sub_data = {
            'id': area.id,
            'name': area.name,
            'subs': []
        }

        # 通读策略步骤1：读缓存redis
        subs = cache.get("sub_area_%d"%area.id)

        if not subs:
            # 通读策略步骤2：读mysql
            # 子级行政区
            sub_areas = area.subs.all()
            sub_data['subs'] = []

            for sub_area in sub_areas:
                # sub_area是子级行政区Area对象
                sub_data['subs'].append({
                    'id': sub_area.id,
                    'name': sub_area.name
                })
            # 通读策略步骤3：缓存回填
            # "sub_area_440000" : [{}....]
            cache.set(
                "sub_area_%d"%area.id,
                sub_data['subs'],
                3600
            )
        else:
            # 如果缓存读到了，则把响应参数中的subs重新赋值为缓存读到读子级行政区数据
            sub_data['subs'] = subs

        # 4、构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'sub_data': sub_data
        })



















