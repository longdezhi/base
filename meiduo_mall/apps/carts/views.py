from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from django_redis import get_redis_connection
import json


from apps.goods.models import SKU
from meiduo_mall.utils.cookiesecret import CookieSecret
# Create your views here.



class CartsView(View):

    # 展示购物车
    def get(self, request):
        user = request.user
        # 约定，不管是从redis还是从cookie中读到的购物车数据
        # 统一组织成购物车字典格式，便于后续操作
        # cart_dict = {1: {"count": 5, "selected": True}}
        cart_dict = {}

        if user.is_authenticated:
            # 从redis中读购物车数据
            conn = get_redis_connection('carts')
            # 商品id和数量数据
            # {b"1": b"5", b"2": b"15"}
            skus_dict = conn.hgetall('carts_%s'%user.id)
            # 勾选状态
            # [b"1", b"2"]
            skus_selected = conn.smembers('selected_%d'%user.id)
            for k,v in skus_dict.items():
                # k: b"1"; v: b"5"
                cart_dict[int(k)] = {
                    "count": int(v),
                    "selected": k in skus_selected # b"1" in [b"1", b"2"] --> True
                }
        else:
            # 从cookie中读购物车数据
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                cart_dict = CookieSecret.loads(cookie_carts.encode())

        cart_skus = []
        # 根据cart_dict字典数据，查找sku商品详细信息
        for k,v in cart_dict.items():
            # k: 1; v: {"count": 5, "selected": True}
            sku = SKU.objects.get(pk=k)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'count': v['count'],
                'selected': v['selected']
            })

        # 构建响应
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'cart_skus': cart_skus
        })


    # 添加购物车
    def post(self, request):
        # 有可能是登陆的User，有可能是未登陆的AnonymousUser
        user = request.user

        # 1、提取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)

        # 2、校验参数
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'}, status=400)

        try:
            SKU.objects.get(pk=sku_id, is_launched=True)
        except SKU.DoesNotExist as e:
            print(e)
            return JsonResponse({'code': 404, 'errmsg': 'sku不存在'}, status=404)

        try:
            # count = int("5")
            count = int(count)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 404, 'errmsg': 'count参数有误'}, status=400)

        if not isinstance(selected, bool):
            return JsonResponse({'code': 404, 'errmsg': 'selected参数有误'}, status=400)


        # 3、数据/业务处理
        if user.is_authenticated:
            # 3.1、用户登陆，存redis
            conn = get_redis_connection('carts')
            # 3.1.1、redis添加sku商品和数量信息
            # hincrby carts_1 sku_id count --> sku_id不再哈希里面则新增，否则累加
            conn.hincrby(
                'carts_%d' % user.id,
                sku_id,
                count
            )
            # 3.1.2、当前sku商品选中状态
            if selected:
                conn.sadd('selected_%d'%user.id, sku_id)
            else:
                conn.srem('selected_%d'%user.id, sku_id)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})

        else:
            # 3.2、用户未登陆，存cookie
            # 约定：购物车字符串数据在cookie中存的时候是以"carts"作为key的
            # {"carts": "AnjBHJBnvjfkmrlngwjtNJKMLNJvgergr="}
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 3.2.1、判断当前请求的cookie里面有没有购物车
                # 解码cookie购物数据
                cart_dict = CookieSecret.loads(cookie_carts.encode())
                # 3.2.1.1、判断当前新增的sku商品在不在原来的cookie购物车中，如果在则累加，不再则新建
                if sku_id in cart_dict:
                    # 累加
                    cart_dict[sku_id]['count'] += count
                    cart_dict[sku_id]['selected'] = selected
                else:
                    # 新增
                    cart_dict[sku_id] = {
                        'count': count,
                        'selected': selected
                    }
            else:
                # 3.2.2、如果购物车数据不存在
                cart_dict = {}
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            # 编码购物车字典数据
            cookie_str = CookieSecret.dumps(cart_dict)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie(
                'carts',
                cookie_str
            )
            return response


    # 修改购物车
    def put(self, request):
        user = request.user

        # 1、提取参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)

        # 2、校验参数
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'}, status=400)

        try:
            SKU.objects.get(pk=sku_id, is_launched=True)
        except SKU.DoesNotExist as e:
            print(e)
            return JsonResponse({'code': 404, 'errmsg': 'sku不存在'}, status=404)

        try:
            # count = int("5")
            count = int(count)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 404, 'errmsg': 'count参数有误'}, status=400)

        if not isinstance(selected, bool):
            return JsonResponse({'code': 404, 'errmsg': 'selected参数有误'}, status=400)


        # 3、业务/数据处理 —— 修改redis or 修改cookie
        if user.is_authenticated:
            # 登陆状态,修改redis购物车数据
            conn = get_redis_connection('carts')
            # 商品数据：hash对象{16: 4}; 勾选状态：集合[16]
            conn.hset(
                'carts_%d' % user.id,
                sku_id,
                count
            )
            if selected:
                conn.sadd('selected_%d'%user.id, sku_id)
            else:
                conn.srem('selected_%d' % user.id, sku_id)

            return JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'cart_sku': {
                    'sku_id': sku_id,
                    'count': count,
                    'selected': selected
                }
            })

        else:
            # 未登陆，修改cookie购物车数据
            # 购物车字典格式{1: {"count": 5, "selected": True}}
            cart_dict = None # 改变是用来记录cookie中解码出来的购物车字典数据，如果cookie没有购物车该变量设置为空字典
            cookie_carts = request.COOKIES.get('carts') # "ASjibgrehgbBHBHlbgre=" or None
            if cookie_carts:
                cart_dict = CookieSecret.loads(cookie_carts.encode()) # 解码得出字典数据
            else:
                cart_dict = {}

            # 修改购物车字典数据，重新写入cookie返回
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 编码购物车数据设置到cookie中
            cookie_carts = CookieSecret.dumps(cart_dict)
            response = JsonResponse({
                'code': 0,
                'errmsg': 'ok',
                'cart_sku': {
                    'sku_id': sku_id,
                    'count': count,
                    'selected': selected
                }
            })
            response.set_cookie(
                'carts',
                cookie_carts
            )
            return response


    # 删除购物车
    def delete(self, request):
        user = request.user
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')

        if user.is_authenticated:
            # 1、登陆，删除redis购物车
            # 商品和数量哈希对象：carts_1 : {1: 5}
            # 选中状态集合对象：[1]
            conn = get_redis_connection('carts')
            conn.hdel('carts_%d'%user.id, sku_id)
            conn.srem('selected_%d'%user.id, sku_id)
            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            # 2、未登陆，删除cookie购物车
            # 2.1、先读cookie购物车数据
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                # 2.2、解码出购物车字典格式数据
                cart_dict = CookieSecret.loads(cookie_carts.encode())
            else:
                cart_dict = {}

            # 2.3、在字典数据中删除当前sku商品
            # del cart_dict[sku_id] or cart_dict.pop(sku_id) # 如果key不存在会报异常KeyError
            try:
                cart_dict.pop(sku_id)
            except KeyError as e:
                print(e)
                return JsonResponse({'code': 400, 'errmsg': '删除错误！'})

            # 2.4、重新编码写入cookie
            cookie_carts = CookieSecret.dumps(cart_dict)
            response = JsonResponse({'code': 0, 'errmsg': 'ok！'})
            response.set_cookie(
                'carts',
                cookie_carts
            )
            return response




class CartsSelectAllView(View):

    def put(self, request):
        # 1、提取参数
        data = json.loads(request.body.decode())
        selected = data.get('selected', True)
        # 2、校验参数
        if not isinstance(selected, bool):
            return JsonResponse({
                'code': 400,
                'errmsg': '参数有误'
            }, status=400)


        # 3、业务/数据处理 —— 根据selected将所有的sku商品勾选状态设置为True or False
        user = request.user
        if user.is_authenticated:
            # 已登陆
            conn = get_redis_connection('carts')
            # (1)、获取当前购物车中的所有的sku商品
            # cart_dict = {b'1': b'5'}
            cart_dict = conn.hgetall('carts_%d'%user.id)
            # sku_ids = [b'1', b'2']
            sku_ids = cart_dict.keys()
            # (2)、把全部sku的id从选中状态的集合中添加/删除
            if selected:
                # sadd('selected_%d'%user.id,  b'1', b'2'...)
                conn.sadd('selected_%d'%user.id, *sku_ids)
            else:
                conn.srem('selected_%d'%user.id, *sku_ids)

            return JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            # 未登陆
            # (1)、提取cookie中的购物车数据
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                cart_dict = CookieSecret.loads(cookie_carts.encode())
            else:
                cart_dict = {}

            # cart_dict = {1: {"count":5, "selected": True}}
            # (2)、设置cookie购物车中商品的状态
            # sku_ids = [1, 2...]
            sku_ids = cart_dict.keys()
            for sku_id in sku_ids:
                cart_dict[sku_id]['selected'] = selected

            # (3)、重新编码cookie购物车数据
            cookie_carts = CookieSecret.dumps(cart_dict)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie(
                'carts',
                cookie_carts
            )

            return response



# 简单购物车展示
class CartsSimpleView(View):

    def get(self, request):

        user = request.user

        # 约定一个购物车字典
        cart_dict = {} # {1: {"count": 5, "selected": True}}

        if user.is_authenticated:
            conn = get_redis_connection('carts')
            # {b'1': b'5'}
            redis_cart_dict = conn.hgetall('carts_%d'%user.id)
            # [b'1']
            redis_selected = conn.smembers('selected_%d'%user.id)

            for k,v in redis_cart_dict.items():
                # k: b'1'；  v: b'5'
                cart_dict[int(k)] = {
                    'count': int(v),
                    'selected': k in redis_selected
                }
        else:
            cookie_carts = request.COOKIES.get('carts')
            if cookie_carts:
                cart_dict = CookieSecret.loads(cookie_carts)


        sku_ids = cart_dict.keys()
        cart_skus = []
        for sku_id in sku_ids:
            if cart_dict[sku_id]['selected']:
                sku = SKU.objects.get(pk=sku_id)
                cart_skus.append({
                    'id': sku.id,
                    'name': sku.name,
                    'count': cart_dict[sku_id]['count'],
                    'default_image_url': sku.default_image.url
                })

        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'cart_skus': cart_skus
        })






















