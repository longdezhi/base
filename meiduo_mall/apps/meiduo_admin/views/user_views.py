

from rest_framework.generics import ListCreateAPIView
from ..serializers.user_serializsers import *
from ..paginations import MyPage


class UserView(ListCreateAPIView):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserModelSerializer

    pagination_class = MyPage

    def get_queryset(self):
        # 根据查询字符串参数keyword过滤
        # 1、提取keyword
        # 问题：如何在非视图函数中获取请求对象？！
        # 答：在django/drf中，每次请求的时候，框架除了把请求对象request传入视图函数以外
        # 还会把请求对象封装到self.request中(self指的是视图对象)
        keyword = self.request.query_params.get('keyword')
        # 2、根据keyword过滤
        if keyword:
            return self.queryset.filter(username__contains=keyword)
        return self.queryset.all() # 获取最新数据










