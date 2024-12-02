from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from common.constants import SaleStatus, OrderStatus
from .models import Order, OrderItem
from api.shop.models import Product
from api.payment.views import delete_paypay_qr_code


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
from ..user.models import UserAddress

logger = logging.getLogger(__name__)

# check ページの支払いボタンには注文情報が保存され、注文ステータスは未払いです。
@api_view(['POST'])
# @line_auth_required
def create_order(request):
    logger.info("=== Starting order creation ===")
    # user_id = request.line_user_id
    user_id ="Uf1e196438ad2e407c977f1ede4a39580"
    if not user_id:
        return Response({'error': 'User ID is required'}, status=400)
    try:
        request_product_list = request.data.get('product_list', None)

        if not request_product_list:
            response = {
                "status": "error",
                "message": "商品が選択されていません。",
                "errors": [],
                "data": {}
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        product_list = []
        product_total_price = 0
        for shop in request_product_list:
            product = Product.objects.filter(product_id=shop["product_id"]).first()
            if not product or product.deleted_flag is True:
                response = {
                    "status": "error",
                    "message": f"商品ID {shop['product_id']} が存在しません。",
                    "errors": [],
                    "data": {}
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            if product.sale_status == SaleStatus.STOP_SALE:
                response = {
                    "status": "error",
                    "message": f"商品 {product.product_name} は現在販売停止中です。",
                    "errors": [],
                    "data": {}
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            item_data = {
                'item_id': str(ulid.new()),
                'order_id': None,
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_price': product.product_price,
                'account': int(shop["quantity"]),
                'deleted_flag': False,
                'subtotal': product.product_price * int(shop["quantity"]),
                'created_by': user_id
            }

            product_list.append(item_data)

            # 在庫確認（必要に応じて）
            # 商品価格の計算
            product_total_price += product.product_price * shop["quantity"]

        # 配送料の計算 (固定値を設定)
        shippingFee = 100
        total_price = product_total_price + shippingFee

        # get default address
        default_address = UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).first()

        if default_address is None:
            response = {
                "status": "error",
                "message": "あすすめの住所は存在しません",
                "errors": [],
                "data": {}
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


        order_data = {
            'order_id': str(ulid.new()),
            'user_id': user_id,
            'order_date': timezone.now(),
            'name': default_address.last_name + ' ' + default_address.first_name,
            'name_katakana': default_address.last_name_katakana + ' ' + default_address.first_name_katakana,
            'phone_number': default_address.phone_number,
            'address': default_address.prefecture_address + default_address.city_address + default_address.district_address + default_address.detail_address,
            'postal_code': default_address.postal_code,
            'carriage': shippingFee,
            'total_price': product_total_price,
            'status': OrderStatus.PENDING_PAYMENT.value,
            'deleted_flag': False,
            # 'tracking_number': '111',
            'created_by': user_id,
            'payment': total_price,
            # 'payment_qr_code_id': request.data.get('payment_qr_code_id'),
        }

        print(order_data)

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
            if not product_list:
                logger.error("Cart is empty")
                raise serializers.ValidationError("カートが空です")

            # items_data = []
            for item in product_list:
                item['order_id'] = order.order_id

            logger.info(f"Processing order items: {product_list}")

            # Validate and save order items
            item_serializer = OrderItemCreateSerializer(data=product_list, many=True)
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
        # 1. get order data from Order
        order = Order.objects.get(
            order_id=order_id,
            deleted_flag=False
        )

        # 2. get order items data from OrderItem
        order_items = OrderItem.objects.filter(
            order_id=order_id,
            deleted_flag=False
        ).values(
            'product_id',
            'product_name',
            'account',
            'product_price'
        )

        # print result see if order exist or not 
        print(f"Order items query: {order_items.query}")  
        print(f"Found items: {list(order_items)}") 

        # 3. get product pics
        product_ids = [item['product_id'] for item in order_items]
        products = {
            p['product_id']: p['image']
            for p in Product.objects.filter(
                product_id__in=product_ids
            ).values('product_id', 'image')
        }

        # 4. assemble items data 
        items_data = []
        for item in order_items:
            items_data.append({
                'id': item['product_id'],
                'name': item['product_name'],
                'quantity': item['account'],
                'price': item['product_price'],
                'image': products.get(item['product_id'])
            })

        # 5. assemble response data
        data = {
            'orderId': order.order_id,
            'trackingNumber': order.tracking_number,
            'orderStatus': order.status,
            'items': items_data,
            'totalAmount': f'¥{order.total_price:,}' if order.total_price else '¥0',
            'discount': f'¥{order.discount_amount:,}' if order.discount_amount else '¥0',
            'finalAmount': f'¥{order.payment:,}' if order.payment else '¥0',
            'deliveryFee': f'¥{order.carriage:,}' if order.carriage else '¥0',
            'orderDate': order.order_date.strftime('%Y-%m-%d') if order.order_date else None,
            'estimatedDelivery': order.estimated_delivery_date.strftime('%Y-%m-%d') if order.estimated_delivery_date else None,
            'postalCode': order.postal_code,
            'address': order.address,
        }

        return Response({
            'status': 'success',
            'data': data
        })

    except Order.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '注文が見つかりません'
        }, status=404)

# @line_auth_required
@api_view(['GET'])
def get_order_list(request):
    try:
        # user_id = request.line_user_id
        user_id = "Uf1e196438ad2e407c977f1ede4a39580"
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
        order = Order.objects.get(order_id=order_id, deleted_flag=False)
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
@api_view(['PATCH'])
def cancel_order(request, order_id):

    try:

        # 注文情報を取得
        order = Order.objects.get(
            order_id=order_id,
            deleted_flag=False)

        # リクエストデータの検証
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.warning(f"リクエストデータが無効です: {serializer.errors}")

            return Response({
                'status': 'error',
                'message': '無効なデータです',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # PayPay QRコードの処理
        if order.payment_qr_code_id:
            try:
                # QRコードの削除をPayPayに要求
                response = delete_paypay_qr_code(order.payment_qr_code_id)

                # QRコードが存在しない場合も正常として扱う
                if response.get('resultInfo', {}).get('code') not in ['SUCCESS', 'DYNAMIC_QR_NOT_FOUND']:
                    logger.error(f"PayPay QRコード削除失敗: {response}")
                    return Response({
                        'status': 'error',
                        'message': 'QRコードの削除中にエラーが発生しました',
                        'error': response.get('resultInfo', {}).get('message')
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                if 'DYNAMIC_QR_NOT_FOUND' not in str(e):
                    logger.error(f"QRコード削除中にエラーが発生しました。order_id={order_id}, error={str(e)}")
                    return Response({
                        'status': 'error',
                        'message': 'QRコードの削除中にエラーが発生しました',
                        'error': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    logger.warning(f"QRコードが既に存在しません: order_id={order_id}")

        # user_id = request.user_id
        update_data = request.data.copy()
        update_data['updated_by'] = request.user_id if hasattr(request, 'user_id') else None

        # 注文状態をキャンセル(5)に更新
        serializer = OrderUpdateSerializer(order, data=update_data, partial=True)
        if not serializer.is_valid():
            logger.error(f"更新データが無効です: {serializer.errors}")
            return Response({
                'status': 'error',
                'message': '更新データが無効です',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info(f"注文がキャンセルされました。order_id={order_id}")

        return Response({
            'status': 'success',
            'message': '注文がキャンセルされました',
            'data': serializer.data
        })

    except Order.DoesNotExist:
        logger.warning(f"注文が見つかりません。order_id={order_id}")
        return Response({
            'status': 'error',
            'message': '注文が見つかりません'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"注文キャンセル中に予期せぬエラーが発生しました。order_id={order_id}, error={str(e)}")
        return Response({
            'status': 'error',
            'message': 'システムエラーが発生しました',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @line_auth_required
@api_view(['DELETE'])
def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.delete()
    return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
# @line_auth_required
def preview_order(request):
    logger.info("=== Starting get preview order ===")

    product_list = request.data.get('product_list', None)

    if not product_list:
        response = {
            "status": "error",
            "message": "商品が選択されていません。",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    product_total_price = 0
    for shop in product_list:
        product = Product.objects.filter(product_id=shop["product_id"]).first()
        if not product or product.deleted_flag is True:
            response = {
                "status": "error",
                "message": f"商品ID {shop['product_id']} が存在しません。",
                "errors": [],
                "data": {}
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if product.sale_status == SaleStatus.STOP_SALE:
            response = {
                "status": "error",
                "message": f"商品 {product.product_name} は現在販売停止中です。",
                "errors": [],
                "data": {}
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # 在庫確認（必要に応じて）
        # 商品価格の計算
        product_total_price += product.product_price * shop["quantity"]

    # 配送料の計算 (固定値を設定)
    shippingFee = 100
    total_price = product_total_price + shippingFee

    data = {
        "product_total_price": product_total_price,
        "shipping_fee": shippingFee,
        "total_price": total_price
    }

    response = {
        "status": "success",
        "message": "注文情報の事前取得が成功しました。",
        "errors": [],
        "data": data
    }

    return Response(response, status=status.HTTP_200_OK)