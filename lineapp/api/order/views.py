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
from core.middleware.line_auth import line_auth_required


logger = logging.getLogger(__name__)

# check ページの支払いボタンには注文情報が保存され、注文ステータスは未払いです。
@api_view(['POST'])
# @line_auth_required
def create_order(request):
    logger.info("=== Starting order creation ===")
    logger.info(f"User: {request.data.get('userName', 'Unknown')}")
    logger.info(f"Raw request data: {request.data}")

    try:
        # Validate required fields
        required_fields = ['userId', 'total', 'cart', 'shippingFee']
        for field in required_fields:
            if field not in request.data:
                logger.error(f"Missing required field: {field}")
                return Response({
                    'status': 'error',
                    'message': f'必須フィールドが欠けています: {field}'
                }, status=400)
            
        order_data = {
            'order_id': str(ulid.new()),
            'user_id': request.data.get('userId'),
            'order_date': timezone.now(),
            'name': request.data.get('name'),
            'phone_number': request.data.get('phone'),
            'address': request.data.get('address'),
            'postal_code': request.data.get('postalCode'),
            'carriage': request.data.get('shippingFee'),
            'total_price': request.data.get('total'),
            'status': 1,
            'deleted_flag': False,
            'tracking_number': '111',
            'created_by': request.data.get('userName'),
            'payment': request.data.get('total') + request.data.get('shippingFee', 0)
        }
        
        logger.info(f"Processed order data: {order_data}")

        with transaction.atomic():
            # Validate and save order
            order_serializer = OrderCreateSerializer(data=order_data)
            if not order_serializer.is_valid():
                logger.error(f"Order validation errors: {order_serializer.errors}")
                return Response({
                    'status': 'error',
                    'message': '注文データが無効です',
                    'errors': order_serializer.errors
                }, status=400)
            
            order = order_serializer.save()
            logger.info(f"Order created successfully with ID: {order.order_id}")

            # Process cart items
            cart = request.data['cart']
            if not cart:
                logger.error("Cart is empty")
                raise serializers.ValidationError("カートが空です")

            items_data = []
            for item in cart:
                try:
                    item_data = {
                        'item_id': str(ulid.new()),
                        'order_id': order_data['order_id'],
                        'product_id': str(item['id']),
                        'product_name': item['name'],
                        'product_price': int(item.get('price', 0)),
                        'account': int(item.get('quantity', 0)),
                        'subtotal': int(item.get('price', 0)) * int(item.get('quantity', 0)),
                        'created_by': request.data.get('userName', 'system')
                    }
                    items_data.append(item_data)
                except (KeyError, ValueError) as e:
                    logger.error(f"Error processing cart item: {item}, Error: {str(e)}")
                    raise serializers.ValidationError(f"カートアイテムの処理中にエラーが発生しました: {str(e)}")

            logger.info(f"Processing order items: {items_data}")

            # Validate and save order items
            item_serializer = OrderItemCreateSerializer(data=items_data, many=True)
            if not item_serializer.is_valid():
                logger.error(f"Order items validation errors: {item_serializer.errors}")
                raise serializers.ValidationError(item_serializer.errors)
                
            item_serializer.save()
            logger.info("Order items saved successfully")

            # Prepare response
            order_detail = OrderDetailSerializer(order).data
            
            logger.info("=== Order creation completed successfully ===")
            return Response({
                'status': 'success',
                'order_id': order_data['order_id'],
                'message': '注文が正常に作成されました',
                'data': order_detail
            })

    except serializers.ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'データ検証エラー: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return Response({
            'status': 'error',
            'message': f'注文の作成中に予期せぬエラーが発生しました: {str(e)}'
        }, status=500)

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

@line_auth_required
@api_view(['GET'])
def get_order_list(request):
    try:
        user_id = request.line_user_id
  
        if not user_id:
            return Response({'error': 'User ID is required'}, status=400)
        
        logger.info("Accessing get_order_list view")
        orders = Order.objects.filter(user_id=user_id,deleted_flag=False).order_by('-created_at')
        order_list = []

        for order in orders:
            try:
                items = OrderItem.objects.filter(order_id=order.order_id)
                items_summary = ', '.join([f"{item.product_name} x{item.account}" for item in items])
                
                order_data = {
                    "id": order.order_id,
                    "date": order.order_date.strftime("%Y-%m-%d"),
                    "items": items_summary,
                    "total": f"¥{order.total_price:,.0f}",
                    "status": order.status,
                    "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                order_list.append(order_data)
            except Exception as e:
                logger.error(f"Error processing order {order.order_id}: {str(e)}")
                continue

        logger.info(f"Successfully retrieved {len(order_list)} orders")
        response = {
            "status": 200,
            "data": order_list
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in get_order_list: {str(e)}")
        return Response(
            {"status": "error", "message": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
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