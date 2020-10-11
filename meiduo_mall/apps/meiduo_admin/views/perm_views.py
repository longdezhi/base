
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from ..serializers.perm_serializers import *
from ..paginations import MyPage

class PermContentTypeView(ListAPIView):
    queryset = ContentType.objects.all()
    serializer_class = PermContentTypeSerializer

class PermView(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermModelSerializer
    pagination_class  = MyPage

    def get_queryset(self):
        return self.queryset.order_by('pk')