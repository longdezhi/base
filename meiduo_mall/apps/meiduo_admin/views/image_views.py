
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from ..serializers.image_serializers import *
from ..paginations import MyPage

class SKUSimpleView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUSimpleSerializer

class ImageView(ModelViewSet):
    queryset = SKUImage.objects.all()
    serializer_class = ImageModelSerializer
    pagination_class = MyPage