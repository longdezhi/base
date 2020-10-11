"""
合并购物车接口
"""
from meiduo_mall.utils.cookiesecret import CookieSecret
from django_redis import get_redis_connection

def merge_cart_cookie_to_redis(request, response):
    """
    功能：合并购物车
    :param request: 请求对象 -----> 获取cookie购物车数据
    :param response: 响应对象 -----> 删除cookie购物车
    :return: 响应对象
    """
    user = request.user

    # 1、获取cookie购物车数据
    cookie_carts = request.COOKIES.get('carts')
    if cookie_carts:
        cart_dict = CookieSecret.loads(cookie_carts)
    else:
        cart_dict = {}

    # cart_dict = {1: {"count": 5, "selected": True}, 2: {"count": 15, "selected": True}}

    # 2、操作redis把cookie数据合并
    conn = get_redis_connection('carts')
    # redis购物车哈希 = {b'1': b'10'}
    # conn.hset() --> 给redis哈希对象一次设置一个键值对
    # conn.hmset() --> 给redis哈希对象一次设置多个键值对
    cart_redis_dict = {} #  {1: 5, 2: 15}
    sku_ids = cart_dict.keys()
    for sku_id in sku_ids:
        # cart_redis_dict = {1: 5}
        cart_redis_dict[sku_id] = cart_dict[sku_id]['count']
        # 把对应的sku商品的状态设置到redis集合中
        if cart_dict[sku_id]['selected']:
            conn.sadd('selected_%d'%user.id, sku_id) # 如果当前sku在cookie中是选中的，则加入redis集合
    # 存在则覆盖原值， 不存在则新增
    if cart_redis_dict:
        conn.hmset('carts_%d'%user.id, cart_redis_dict)


    # 3、操作响应对象删除cookie购物车返回
    response.delete_cookie('carts')
    return response













