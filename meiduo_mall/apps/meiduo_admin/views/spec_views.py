

from rest_framework.viewsets import ModelViewSet
from ..serializers.spec_serializers import *
from ..paginations import MyPage

class SpecView(ModelViewSet):
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecModelSerializer
    pagination_class = MyPage