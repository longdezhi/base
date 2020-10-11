

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.mixins import UpdateModelMixin
from ..serializers.order_serializers import *
from ..paginations import MyPage

class OrderView(UpdateModelMixin, ReadOnlyModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSimpleSerializer
    pagination_class = MyPage

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(order_id__contains=keyword)
        return self.queryset.all()

    def get_serializer_class(self):
        # 功能：获取操作数据使用序列化器类；默认返回类属性serializer_class
        # 区分2个逻辑
        # (1)、如果调用的是获取列表数据接口self.list, 使用OrderSimpleSerializer
        # (2)、如果调用的是获取单一详情数据接口self.retrieve, 使用OrderDetailSerializer
        # 知识点：self.action属性就是当前请求的视图函数的名称！
        if self.action == "list":
            return OrderSimpleSerializer
        elif self.action == "retrieve":
            return OrderDetailSerializer
        elif self.action == 'partial_update':
            return OrderDetailSerializer

        return self.get_serializer_class








