from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MyPage(PageNumberPagination):
    page_query_param = 'page' # ?page=1
    page_size_query_param = 'pagesize' # ?pagesize=5
    max_page_size = 10
    page_size = 5

    def get_paginated_response(self, data):
        return Response({
            'counts': self.page.paginator.count, # 总数量
            'lists': data, # 查询集分页的子集(当前页数据)
            'page': self.page.number, # 当前页
            'pages': self.page.paginator.num_pages, # 总页数
            'pagesize': self.page_size
        })