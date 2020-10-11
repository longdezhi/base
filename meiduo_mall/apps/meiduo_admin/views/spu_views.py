
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from ..serializers.spu_serializers import *
from ..paginations import MyPage


class SPUCateSimpleView(ListAPIView):
    queryset = GoodsCategory.objects.all()
    serializer_class = SPUCateSimpleSerializer

    def get_queryset(self):
        parent_id = self.kwargs.get('pk')
        # 如果是二级、三级分类接口调用，根据路径pk过滤出子集返回
        if parent_id:
            return self.queryset.filter(parent_id=parent_id)

        # 如果是一级分类接口调用
        return self.queryset.filter(parent=None)


class BrandSimpleView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSimpleSerializer


class SPUView(ModelViewSet):
    queryset = SPU.objects.all()
    serializer_class = SPUModelSerializer
    pagination_class = MyPage

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)
        return self.queryset.all()