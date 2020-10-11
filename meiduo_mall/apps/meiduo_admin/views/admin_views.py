
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from ..serializers.admin_serializers import *
from ..paginations import MyPage

class AdminGroupView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = AdminGroupSerializer

class AdminUserView(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminUserSerializer
    pagination_class = MyPage