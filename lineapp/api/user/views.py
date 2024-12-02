import logging
from datetime import datetime

import ulid
from django.shortcuts import render
from rest_framework.decorators import api_view

from api.user.models import UserAddress
from api.user.serializers import UserAddressSerializer
from rest_framework import status
from rest_framework.response import Response

from core.middleware.line_auth import line_auth_required

logger = logging.getLogger(__name__)

@api_view(['GET'])
# @line_auth_required
def get_address_list(request):

    logger.info("----------------get_address_list-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'


    user_address_list = UserAddress.objects.filter(user_id=user_id, deleted_flag=False)

    address_list = []
    if user_address_list:
        for user_address in user_address_list:
            address_info = {
                "address_id": user_address.address_id,
                "last_name": user_address.last_name,
                "first_name": user_address.first_name,
                "phone_number": user_address.phone_number,
                "prefecture_address": user_address.prefecture_address,
                "city_address": user_address.city_address,
                "district_address": user_address.district_address,
                "detail_address": user_address.detail_address,
                "postal_code": user_address.postal_code,
                "is_default": user_address.is_default,
            }
            address_list.append(address_info)

    response = {
        'status': 'success',
        "message": "住所の一览情報が正常に取得されました。",
        "errors": [],
        "data": {
            "address_list": address_list
        }
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
# @line_auth_required
def get_address_detail(request, address_id):

    logger.info("----------------get_address_detail-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    if address_id is None:
        message = {
            'status': 'error',
            "message": "address_id はなし",
            "errors": [{
                "code": 404,
                "message": "address_id はなし"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    result = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()

    address_info = {}
    if result:
        address_info = {
            "address_id": result.address_id,
            "last_name": result.last_name,
            "first_name": result.first_name,
            "last_name_katakana": result.last_name_katakana,
            "first_name_katakana": result.first_name_katakana,
            "phone_number": result.phone_number,
            "prefecture_address": result.prefecture_address,
            "city_address": result.city_address,
            "district_address": result.district_address,
            "detail_address": result.detail_address,
            "postal_code": result.postal_code,
            "is_default": result.is_default,
        }

    response = {
        'status': 'success',
        "message": "住所詳細情報が正常に取得されました。",
        "errors": [],
        "data": {
            "address_detail": address_info
        }
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['PATCH'])
# @line_auth_required
def set_default_address(request, address_id):

    logger.info("----------------set_default_address-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    if address_id is None:
        message = {
            'status': 'error',
            "message": "address_idはなし",
            "errors": [{
                "code": 404,
                "message": "address_idはなし"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    address_info = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()

    if address_info is None:
        message = {
            'status': 'error',
            "message": "住所が存在しません",
            "errors": [{
                "code": 404,
                "message": "住所が存在しません"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).update(is_default=False)

    UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).update(is_default=True)

    response = {
        'status': 'success',
        "message": "デフォルト住所が正常に設定されました。",
        "errors": [],
        "data": {}
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
# @line_auth_required
def get_default_address(request):

    logger.info("----------------get_default_address-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    result = UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).first()

    address_info = {}
    if result:
        address_info = {
            "address_id": result.address_id,
            "last_name": result.last_name,
            "first_name": result.first_name,
            "last_name_katakana": result.last_name_katakana,
            "first_name_katakana": result.first_name_katakana,
            "phone_number": result.phone_number,
            "prefecture_address": result.prefecture_address,
            "city_address": result.city_address,
            "district_address": result.district_address,
            "detail_address": result.detail_address,
            "postal_code": result.postal_code,
            "is_default": result.is_default,
        }

    response = {
        "status": "success",
        "message": "デフォルト住所情報が正常に取得されました。",
        "errors": [],
        "data": {
            "address_detail": address_info
        }
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['PUT'])
# @line_auth_required
def update_address(request, address_id):

    logger.info("----------------update_address-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    try:
        user_address = UserAddress.objects.get(address_id=address_id)
    except UserAddress.DoesNotExist:
        return Response({
            "error"
            "message": "住所が見つかりませんでした。",
            "errors": [],
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = UserAddressSerializer(user_address, data=request.data, context={'user_id': user_id})

    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "住所が正常に更新されました。",
            "errors": [],
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "error",
        "message": "住所更新失敗",
        "errors": serializer.errors,
        "data": {}
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# @line_auth_required
def create_address(request):

    logger.info("----------------create_address-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    logger.info("request body data: {}".format(request.data))
    logger.info("user_id: {}".format(user_id))

    serializer = UserAddressSerializer(data=request.data, context={'user_id': user_id})

    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "住所が正常に作成されました。",
            "errors": [],
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "message": "住所作成失敗",
        "errors": serializer.errors,
        "data": {}
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
# @line_auth_required
def delete_address(request, address_id):

    logger.info("----------------delete_address-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    logger.info("user_id: {}".format(user_id))

    if address_id is None:
        message = {
            "status": "error",
            "message": "address_id はなし",
            "errors": [{
                "code": 404,
                "message": "address_id はなし"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    address_info = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()

    if address_info is None:
        message = {
            "status": "error",
            "message": "住所が存在しません",
            "errors": [{
                "code": 404,
                "message": "住所が存在しません"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).update(deleted_flag=True)

    response = {
        "status": "success",
        "message": "住所が正常に削除されました。",
        "errors": [],
        "data": {}
    }
    return Response(response, status=status.HTTP_200_OK)
