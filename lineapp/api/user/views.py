import logging
from datetime import datetime

import ulid
from django.shortcuts import render
from rest_framework.decorators import api_view

from api.user.models import UserAddress
from api.user.serializers import UserAddressSerializer
# from common.base_view import BaseAPIView
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

@api_view(['GET'])
# @line_auth_required
def get_address_list(request):

    # user_id = request.user_id
    user_id = "01JCQFAYQW3W54S7P3PPM4M7DG"
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

    # user_id = request.user_id
    user_id = "01JCQFAYQW3W54S7P3PPM4M7DG"

    if address_id is None:
        message = {
            "message": "address_id is None",
            "errors": [{
                "code": 404,
                "message": "address_id is None"
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

    # user_id = request.user_id
    user_id = "01JCQFAYQW3W54S7P3PPM4M7DG"

    if address_id is None:
        message = {
            'status': 'error',
            "message": "address_id is None",
            "errors": [{
                "code": 404,
                "message": "address_id is None"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    address_info = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()

    if address_info is None:
        message = {
            'status': 'error',
            "message": "address is not exist",
            "errors": [{
                "code": 404,
                "message": "address is not exist"
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

    # user_id = request.user_id
    user_id = "01JCQFAYQW3W54S7P3PPM4M7DG"

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

    # user_id = request.user_id
    user_id = "01JCQFAYQW3W54S7P3PPM4M7DG"

    try:
        user_address = UserAddress.objects.get(address_id=address_id)
    except UserAddress.DoesNotExist:
        return Response({
            "message": "住所が見つかりませんでした。",
            "errors": [],
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = UserAddressSerializer(user_address, data=request.data, context={'user_id': user_id})

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "住所が正常に更新されました。",
            "errors": [],
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "message": "住所更新失敗",
        "errors": serializer.errors,
        "data": {}
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# @line_auth_required
def create_address(request):
    # user_id = request.user_id
    user_id = '01JCQFAYQW3W54S7P3PPM4M7DG'
    print(request.data)
    print(user_id)

    serializer = UserAddressSerializer(data=request.data, context={'user_id': user_id})

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "住所が正常に作成されました。",
            "errors": [],
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "message": "住所作成失敗",
        "errors": serializer.errors,
        "data": {}
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
# @line_auth_required
def delete_address(request, address_id):

    # user_id = request.user_id
    user_id = "01JCQFAYQW3W54S7P3PPM4M7DG"

    if address_id is None:
        message = {
            "message": "address_id is None",
            "errors": [{
                "code": 404,
                "message": "address_id is None"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    address_info = UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).first()

    if address_info is None:
        message = {
            "message": "address is not exist",
            "errors": [{
                "code": 404,
                "message": "address is not exist"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    UserAddress.objects.filter(address_id=address_id, user_id=user_id, deleted_flag=False).update(deleted_flag=True)

    response = {
        "message": "住所が正常に削除されました。",
        "errors": [],
        "data": {}
    }
    return Response(response, status=status.HTTP_200_OK)