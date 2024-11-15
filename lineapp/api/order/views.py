from django.shortcuts import get_object_or_404
from rest_framework import serializers  
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Order, OrderItem
from django.db import transaction
from .serializers import (
    OrderCreateSerializer, 
    OrderUpdateSerializer, 
    OrderDetailSerializer,
    OrderItemCreateSerializer
)
import ulid
import logging
from api.line_auth import line_auth_required


logger = logging.getLogger(__name__)

# check ページの支払いボタンには注文情報が保存され、注文ステータスは未払いです。
@api_view(['POST'])
# @line_auth_required
def create_order(request):
    logger.info(f"CREATE ORDER: {request.data.get('userName', 'Unknown')}")
    logger.info("CREATE ORDER data: {request.data}")

    order_data = {
        'order_id': str(ulid.new()),
        'user_id': request.data.get('userId'),
        'order_date': timezone.now(),  
        'express_information': request.data.get('express_information'),
        'carriage': request.data.get('shippingFee'),
        'total_price': request.data.get('total'),
        'status': 1,  
        # test
        'tracking_number': '111',  
        'created_by': request.data.get('userName'),
        'payment': request.data.get('total') + request.data.get('shippingFee', 0)  
    }
    logger.info(f"处理后的订单数据: {order_data}") 
    try:
        with transaction.atomic():
            order_serializer = OrderCreateSerializer(data=order_data)
            if not order_serializer.is_valid():
                logger.error(f"订单数据验证错误: {order_serializer.errors}")
                return Response({
                    'status': 'error',
                    'message': '注文データが無効です',
                    'errors': order_serializer.errors
                }, status=400)
            
            order = order_serializer.save()

            cart = request.data.get('cart', [])
            logger.info(f"Cart data: {cart}") 
            # create order-item 
            items_data = []
            for item in cart:
                item_data = {
                    'order_id': order_data['order_id'],
                    'product_id': str(item.get('id')),  
                    'product_name': item.get('name'),
                    'product_price': int(item.get('price', 0)),  
                    'account': int(item.get('quantity', 0)),  
                    'subtotal': int(item.get('price', 0)) * int(item.get('quantity', 0)),
                    'created_by': request.data.get('userName')
                }
                items_data.append(item_data)
            logger.info(f"Items data: {items_data}")  

            item_serializer = OrderItemCreateSerializer(data=items_data, many=True)
            if not item_serializer.is_valid():
                logger.error(f"注文アイテムのバリデーションエラー: {item_serializer.errors}")
                raise serializers.ValidationError(item_serializer.errors)
            item_serializer.save()

            order_detail = OrderDetailSerializer(order).data
            
            return Response({
                'status': 'success',
                'order_id': order_data['order_id'],
                'message': '注文が正常に作成されました',
                'data': order_detail
            })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'注文の作成中にエラーが発生しました: {str(e)}'
        }, status=400)

# @line_auth_required
@api_view(['GET'])
def get_order_detail(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, deleted_flag=False)
        serializer = OrderDetailSerializer(order)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    except Order.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '注文が見つかりません'
        }, status=404)

# @line_auth_required
@api_view(['GET'])
def get_order_list(request):
    orders = Order.objects.all()
    order_list = []

    for order in orders:
        items = OrderItem.objects.filter(order_id=order.order_id)
        items_summary = ', '.join([f"{item.product_name} x{item.account}" for item in items])
        
        order_data = {
            "id": order.order_id,
            "date": order.order_date.strftime("%Y-%m-%d"),
            "items": items_summary,
            "total": f"¥{order.total_price:,.0f}"
        }
        order_list.append(order_data)

    return JsonResponse(order_list, safe=False)

# @line_auth_required
@api_view(['PATCH'])
def update_order(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '注文が更新されました',
                'data': OrderDetailSerializer(order).data
            })
        return Response({
            'status': 'error',
            'message': '無効なデータです',
            'errors': serializer.errors
        }, status=400)
    except Order.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '注文が見つかりません'
        }, status=404)

# @line_auth_required
@api_view(['DELETE'])
def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.delete()
    return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)