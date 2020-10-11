
from django.urls import re_path
# obtain_jwt_token视图用于校验username和password并签发token；视图默认响应参数只有token
from rest_framework_jwt.views import obtain_jwt_token
from .views.login_views import *
from .views.home_views import *
from .views.user_views import *
from .views.sku_views import *
from .views.spu_views import *
from .views.spec_views import *
from .views.option_views import *
from .views.image_views import *
from .views.order_views import *
from .views.perm_views import *
from .views.group_views import *
from .views.admin_views import *

urlpatterns = [
    # re_path(r'^authorizations/$', LoginView.as_view()),
    re_path(r'^authorizations/$', obtain_jwt_token),

    # 1、用户总数统计
    re_path(r'^statistical/total_count/$', UserTotalCountView.as_view()),
    # 2、统计当日新增用户
    re_path(r'^statistical/day_increment/$', UserDayCountView.as_view()),
    # 3、日活跃用户统计
    re_path(r'^statistical/day_active/$', UserActiveCountView.as_view()),
    # 4、日下单用户统计
    re_path(r'^statistical/day_orders/$', UserOrderCountView.as_view()),
    # 5、月增用户统计
    re_path(r'^statistical/month_increment/$', UserMonthCountView.as_view()),

    # 6、日分类商品访问量统计
    re_path(r'^statistical/goods_day_views/$', GoodsDayView.as_view()),

    # 用户管理
    re_path(r'^users/$', UserView.as_view()),

    # SKU管理
    re_path(r'^skus/$', SKUGoodsView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^skus/(?P<pk>\d+)/$', SKUGoodsView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 新增SKU可选三级分类
    re_path(r'^skus/categories/$', SKUCategoryView.as_view()),
    # 新增SKU可选SPU
    re_path(r'^goods/simple/$', SPUSimpleView.as_view()),
    # 新增SKU可选规格和选项信息
    re_path(r'^goods/(?P<pk>\d+)/specs/$', SPUSpecView.as_view()),

    # SPU管理
    re_path(r'^goods/$', SPUView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^goods/(?P<pk>\d+)/$', SPUView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),

    # 新增SPU可选品牌
    re_path(r'^goods/brands/simple/$', BrandSimpleView.as_view()),
    # 新增SPU可选一级分类
    re_path(r'^goods/channel/categories/$', SPUCateSimpleView.as_view()),
    # 新增SPU可选二级或三级份额里
    re_path(r'^goods/channel/categories/(?P<pk>\d+)/$', SPUCateSimpleView.as_view()),

    # 规格管理
    re_path(r'^goods/specs/$', SpecView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^goods/specs/(?P<pk>\d+)/$', SpecView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 选项管理
    re_path(r'^specs/options/$', OptionView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^specs/options/(?P<pk>\d+)/$', OptionView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 新增选项可选规格
    re_path(r'^goods/specs/simple/$', OptSpecSimpleView.as_view()),

    # 图片管理
    re_path(r'^skus/images/$', ImageView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^skus/images/(?P<pk>\d+)/$', ImageView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 新增图片可选SKU
    re_path(r'^skus/simple/$', SKUSimpleView.as_view()),

    # 订单管理
    re_path(r'^orders/$', OrderView.as_view({'get':'list'})),
    re_path(r'^orders/(?P<pk>\d+)/$', OrderView.as_view({'get':'retrieve'})),
    re_path(r'^orders/(?P<pk>\d+)/status/$', OrderView.as_view({'patch':'partial_update'})),

    # 权限管理
    re_path(r'^permission/perms/$', PermView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^permission/perms/(?P<pk>\d+)/$', PermView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 新增权限可选类型
    re_path(r'^permission/content_types/$', PermContentTypeView.as_view()),

    # 分组管理
    re_path(r'^permission/groups/$', GroupView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^permission/groups/(?P<pk>\d+)/$', GroupView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    # 新增分组可选权限
    re_path(r'^permission/simple/$', GroupPermView.as_view()),

    re_path(r'^permission/admins/$', AdminUserView.as_view({'get': 'list', 'post': 'create'})),
    re_path(r'^permission/admins/(?P<pk>\d+)/$', AdminUserView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),

    re_path(r'^permission/groups/simple/$', AdminGroupView.as_view()),
]



