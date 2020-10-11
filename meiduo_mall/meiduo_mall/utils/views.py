

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        # 该函数返回值就是没有登陆的时候，视图的返回
        return JsonResponse({'code': 400, 'errmsg': '未登陆'}, status=401)