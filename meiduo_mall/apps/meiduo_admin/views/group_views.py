
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from ..serializers.group_serializers import *
from ..paginations import MyPage

class GroupPermView(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = GroupPermSimpleSerializer

class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupModelSerializer
    pagination_class = MyPage