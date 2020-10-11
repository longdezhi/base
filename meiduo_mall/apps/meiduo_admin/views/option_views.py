

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from ..serializers.option_serializers import *
from ..paginations import MyPage


class OptSpecSimpleView(ListAPIView):
    queryset = SPUSpecification.objects.all()
    serializer_class = OptSpecSimpleSerializer

class OptionView(ModelViewSet):
    queryset = SpecificationOption.objects.all()
    serializer_class = OptionModelSerializer
    pagination_class = MyPage