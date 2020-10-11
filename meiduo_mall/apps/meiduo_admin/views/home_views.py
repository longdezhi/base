"""
主页接口视图
"""
from django.utils import timezone # Django提供用于处理时间的一个模块

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.users.models import User
from apps.orders.models import OrderInfo

from datetime import timedelta

# 1、用户总数
class UserTotalCountView(APIView):

    def get(self, request):
        # 1、提取参数
        # 2、校验参数
        # 3、数据处理 —— 统计用户总数量
        count = User.objects.count()
        # 4、构建响应
        # cur_date = datetime.now() # 系统本地时间
        cur_date = timezone.localtime() # 获取配置参数TIME_ZONE指定时区的时间；返回datetime对象
        return Response({
            'count': count,
            'date': cur_date.date() # 年月日; datetime().date() --> 把datetime类型转化为date类型(只取年月日)
        })


# 2、日增用户数量统计
class UserDayCountView(APIView):

    def get(self, request):
        # 当日新增用户数量统计：过滤出"当日"新建的用户数量 date_joined>=当日的零时刻
        # 思考：如何获取"当日"的零时刻？！
        cur_time = timezone.localtime() # datetime(2020, 9, 26, 17, 8, 56, 612345, tz=<Asia/Shanghai>)
        # replace函数把原datetime对象的年月日是分秒微妙和时区属性替换，返回替换后的一个新的datetime对象
        cur_0_time = cur_time.replace(hour=0, minute=0, second=0, microsecond=0)
        count = User.objects.filter(
            date_joined__gte=cur_0_time
        ).count()

        return Response({
            'count': count,
            'date': cur_time.date()
        })


# 3、日活跃用户统计
class UserActiveCountView(APIView):

    def get(self, request):
        cur_0_time = timezone.localtime().replace(
            hour=0, minute=0, second=0
        )

        count = User.objects.filter(
            last_login__gte=cur_0_time
        ).count()

        return Response({
            'count': count,
            'date': cur_0_time.date()
        })


# 4、日下单用户量
class UserOrderCountView(APIView):

    def get(self, request):
        # 业务(过滤统计)：当日 下的订单的 用户的 数量；
        # 1、过滤依据条件是什么？答：当日的零时刻 —— 订单表(从)的依据条件
        # 2、查询的目标数据是什么？答：用户(主)数量
        # 分析结论：按照从表的依据条件，查询目标数据是主表数据；
        cur_0_time = timezone.localtime().replace(
            hour=0, minute=0, second=0
        )

        # 方案一：从从表入手查询；
        """
        # 1、先查询出当日下的所有的订单；
        orders = OrderInfo.objects.filter(
            create_time__gte=cur_0_time
        )
        # 2、查询出下这些订单的用户
        users = set()
        for order in orders:
            users.add(order.user)
        count = len(users)
        """

        # 方案二：从主表入手查询;
        users = User.objects.filter(
            # 使用从表的依据条件，过滤查询主表数据；
            # orders为从表关联主表字段中related_name约束条件设置的隐藏字段；
            orders__create_time__gte=cur_0_time
        )
        count = len(set(users))

        return Response({
            'count': count,
            'date': cur_0_time.date()
        })


# 5、月新增用户统计
class UserMonthCountView(APIView):

    def get(self, request):
        # 统计最近30天(包括当日)，其中每一天用户新增数量
        # 1、过滤逻辑：大于等于过去某一天零时刻，小于次日的零时刻
        # 2、获取最新30天(包括当日)其中某一天的零时刻(次日的零时刻=某一天的零时刻+1天)

        # 当日(最后一天的)的零时刻
        end_0_time = timezone.localtime().replace(
            hour=0, minute=0, second=0
        )

        # 启始那一天的0时刻
        # 公式：start_0_time = end_0_time  -  (统计天数-1)
        start_0_time = end_0_time - timedelta(days=29) # 29天

        # [start_0_time, end_0_time]区间表示30天

        ret_list = []
        # 遍历30次，每一次遍历出其中的某一天，然后计算每一天的新增用户数量
        for index in range(30):
            # calc_0_time = start_0_time + timedelta(days=0)    index=0
            # calc_0_time = start_0_time + timedelta(days=1)    index=1
            # calc_0_time = start_0_time + timedelta(days=2)    index=2
            # calc_0_time = start_0_time + timedelta(days=3)    index=3
            # .....
            # calc_0_time = start_0_time + timedelta(days=29)   index=29
            # 公式： calc_0_time = start_0_time + timedelta(days=index)

            # 其中某一天的零时刻
            calc_0_time = start_0_time + timedelta(days=index)
            # 次日的零时刻
            next_0_time = calc_0_time  + timedelta(days=1)

            count = User.objects.filter(
                date_joined__gte=calc_0_time,
                date_joined__lt=next_0_time
            ).count()

            ret_list.append({
                'count': count,
                'date': calc_0_time.date()
            })

        return Response(ret_list)

from ..serializers.home_serializers import *
# 6、获取分类访问量列表数据
class GoodsDayView(ListAPIView):
    # 如果在类属性中获取0时刻，这个cur_0_time记录的永远都是服务器启动的那一天的0时刻了；
    # cur_0_time = timezone.localtime().replace(hour=0, minute=0, second=0)
    # queryset = GoodsVisitCount.objects.filter(
    #     create_time__gte=cur_0_time
    # )

    queryset = GoodsVisitCount.objects.all()
    serializer_class = GoodsVisitModelSerializer

    # 在每一次请求的时候，都是通过get_queryset方法来获取查询集
    def get_queryset(self):
        cur_0_time = timezone.localtime().replace(hour=0, minute=0, second=0)
        return self.queryset.filter(
            create_time__gte=cur_0_time
        )















