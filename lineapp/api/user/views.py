import logging
import ulid
from api.user.models import UserAddress
from api.user.serializers import UserAddressSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from common.exceptions import CustomAPIException
from django.utils.timezone import now


logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_address_list(request):

    logger.info("==========get_address_list=============")
    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX" #for develop

    user_address_list = UserAddress.objects.filter(user_id=user_id, deleted_flag=False)
    serializer = UserAddressSerializer(user_address_list, many=True)

    response = {
        'status': 'success',
        "message": "住所の一覧情報が正常に取得されました。",
        "data": {
            "address_list": serializer.data  
        }
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_address_detail(request, address_id):
    logger.info("==========get_address_detail==========")
    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX" #for develop

    address = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()  
    if not address:
        raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="住所情報が見つかりませんでした。",
                severity="error"
            )
    serializer = UserAddressSerializer(address)
    response = {
        'status': 'success',
        "message": "住所詳細情報が正常に取得されました。",
        "data": {
            "address_detail": serializer.data
        }
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['PATCH']) 
def set_default_address(request, address_id):
    logger.info("==========set_default_address==========")
    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX" #for develop

    UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).update(is_default=False)
    changeAddress = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).update(is_default=True)
    if changeAddress == 1:
        response = {'status': 'success', "message": "デフォルト住所が正常に設定されました。"}
        return Response(response, status=status.HTTP_200_OK)
    else:
           raise CustomAPIException(
                   status=status.HTTP_404_NOT_FOUND,
                   message="デフォルト住所設定が失敗しました。",
                   severity="error"
                   )

@api_view(['GET'])
def get_default_address(request):

    logger.info("==========get_default_address==========")
    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX" #for develop

    address = UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).first()
    if not address:
           raise CustomAPIException(
                   status=status.HTTP_404_NOT_FOUND,
                   message="住所情報が見つかりませんでした。",
                   severity="error"
                   )
    serializer = UserAddressSerializer(address)

    response = {
        "status": "success",
        "message": "デフォルト住所情報が正常に取得されました。",
        "errors": [],
        "data": {
            "address_detail": serializer.data
        }
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_address(request, address_id):

    logger.info("==========update_address==========")
    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX" #for develop

    address = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()
    if not address:
           raise CustomAPIException(
                   status=status.HTTP_404_NOT_FOUND,
                   message="住所情報が見つかりませんでした。",
                   severity="error"
                   )
    serializer = UserAddressSerializer(instance=address, data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        address.last_name = validated_data.get('last_name', address.last_name)
        address.first_name = validated_data.get('first_name', address.first_name)
        address.last_name_katakana = validated_data.get('last_name_katakana', address.last_name_katakana)
        address.first_name_katakana = validated_data.get('first_name_katakana', address.first_name_katakana)
        address.phone_number = validated_data.get('phone_number', address.phone_number)
        address.prefecture_address = validated_data.get('prefecture_address_id', address.prefecture_address)
        address.city_address = validated_data.get('city_address', address.city_address)
        address.district_address = validated_data.get('district_address', address.district_address)
        address.detail_address = validated_data.get('detail_address', address.detail_address)
        address.postal_code = validated_data.get('postal_code', address.postal_code)
        address.created_by = user_id
        address.created_at = now()
        address.updated_by = user_id
        address.updated_at = now()
        address.save()
        return Response({
            "status": "success",
            "message": "住所が正常に更新されました。"
    }, status=status.HTTP_200_OK)
    else:
        raise CustomAPIException(
                   status=status.HTTP_400_BAD_REQUEST,
                   message="住所更新失敗",
                   severity="error"
                   )


@api_view(['POST']) 
def create_address(request):

    logger.info("==========create_address==========")
    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX"
    logger.info("request body data: {}".format(request.data))

    serializer = UserAddressSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        address = UserAddress.objects.create(
                address_id=str(ulid.new()),
                user_id=user_id,
                last_name=validated_data.get('last_name'),
                first_name=validated_data.get('first_name'),
                last_name_katakana=validated_data.get('last_name_katakana'),
                first_name_katakana=validated_data.get('first_name_katakana'),
                phone_number=validated_data.get('phone_number'),
                prefecture_address=validated_data.get('prefecture_address_id'),
                city_address=validated_data.get('city_address'),
                district_address=validated_data.get('district_address'),
                detail_address=validated_data.get('detail_address'),
                postal_code=validated_data.get('postal_code'),
                is_default=False,
                deleted_flag=False,
                created_by=user_id,
                updated_by=user_id
            )
        logger.info("Address created successfully: {}".format(address.address_id))
        return Response({
            "status": "success",
            "message": "住所が正常に作成されました。",
        }, status=status.HTTP_201_CREATED)
    else:
        raise CustomAPIException(
                   status=status.HTTP_400_BAD_REQUEST,
                   message="住所作成が失敗しました",
                   severity="error"
                   )

@api_view(['DELETE'])
def delete_address(request, address_id):

    logger.info("==========delete_address==========")

    user_id = request.user_info.user_id
    # user_id ="01JE5TBDC3G4HKQTC807AV9HTX" #for develop
    logger.info("user_id: {}".format(user_id))

    address_info = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()

    if not address_info:
        raise CustomAPIException(
            status=status.HTTP_404_NOT_FOUND,
            message="住所が存在しません",
            severity="error"
        )

    UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).update(deleted_flag=True)

    response = {
        "status": "success",
        "message": "住所が正常に削除されました。"
    }
    return Response(response, status=status.HTTP_200_OK)
