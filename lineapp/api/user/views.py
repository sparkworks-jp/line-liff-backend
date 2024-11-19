from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer,AddressCreateValidator,UserAddressSerializer
from core.middleware.line_auth import line_auth_required

@api_view(['GET'])
@line_auth_required
def get_user_info(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@line_auth_required
def create_address(request):
    # 入力データの検証
    validator = AddressCreateValidator(data=request.data)
    validator.is_valid(raise_exception=True)
    
    # ユーザーIDを追加
    address_data = validator.validated_data
    address_data['user_id'] = request.user.id
    address_data['created_by'] = request.user.id
    address_data['updated_by'] = request.user.id
    
    # 住所を作成
    serializer = UserAddressSerializer(data=address_data)
    serializer.is_valid(raise_exception=True)
    address = serializer.save()
    
    return Response(serializer.data)