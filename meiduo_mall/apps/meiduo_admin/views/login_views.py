

from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers.loginserializers import LoginSerializer

class LoginView(APIView):

    def post(self, request):
        # 1、提取参数
        # 2、校验参数
        # 3、数据处理
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 4、构建响应
        return Response({
            'token': serializer.validated_data.get('token'),
            'username': serializer.validated_data['user'].username,
            'user_id': serializer.validated_data['user'].id
        })