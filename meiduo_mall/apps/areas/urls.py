

from django.urls import re_path
from . import views

urlpatterns = [
    # 省
    re_path(r'^areas/$', views.ProvinceAreasView.as_view()),
    # 市区
    re_path(r'^areas/(?P<pk>[1-9]\d+)/$', views.SubAreasView.as_view()),
]