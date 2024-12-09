from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from common.constants import SaleStatus, OrderStatus
from common.exceptions import CustomAPIException
from .models import Order, OrderItem
from api.shop.models import Product
from api.payment.views import delete_paypay_qr_code


from django.db import transaction
from .serializers import ( OrderUpdateSerializer, OrderDetailSerializer)
import ulid
import logging
from ..user.models import UserAddress

logger = logging.getLogger(__name__)

def validate_and_prepare_products(product_list, user_id):
    validated_products = []
    total_price = 0

    for item in product_list:
        product = Product.objects.filter(product_id=item['product_id'], deleted_flag=False).first()
        if not product:
            raise serializers.ValidationError(f"商品ID {item['product_id']} が存在しません")
        if product.sale_status == SaleStatus.STOP_SALE:
            raise serializers.ValidationError(f"商品 {product.product_name} は現在販売停止中です")

        quantity = int(item['quantity'])
        subtotal = product.product_price * quantity
        total_price += subtotal

        validated_products.append({
            'item_id': str(ulid.new()),
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_price': product.product_price,
            'account': quantity,
            'subtotal': subtotal,
            'deleted_flag': False,
            'created_by': user_id
        })

    return validated_products, total_price

def prepare_order_items(product_list, order_id, user_id):
    return [
        OrderItem(
            item_id=str(ulid.new()),
            order_id=order_id,
            product_id=item['product_id'],
            product_name=item['product_name'],
            product_price=item['product_price'],
            account=item['account'],
            subtotal=item['subtotal'],
            deleted_flag=False,
            created_by=user_id,
        )
        for item in product_list
    ]

# check ページの支払いボタンには注文情報が保存され、注文ステータスは未払いです。
@api_view(['POST'])
def create_order(request):
    logger.info("=== Starting order creation ===")
    user_id = request.user_info.user_id
    # user_id ="Uf1e196438ad2e407c977f1ede4a39580" //for develop
    
    request_product_list = request.data.get('product_list', None)
    product_list, product_total_price = validate_and_prepare_products(request_product_list, user_id)
    
    # Mock shipping_fee
    shipping_fee = 100 
    total_price = product_total_price + shipping_fee
    
    address = UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).first()

    # DBデータ更新
    with transaction.atomic():
        
        order_data = {
            'order_id': str(ulid.new()),
            'user_id': user_id,
            'order_date': timezone.now(),
            'name': f"{address.last_name} {address.first_name}",
            'name_katakana': f"{address.last_name_katakana} {address.first_name_katakana}",
            'phone_number': address.phone_number,
            'address': f"{address.prefecture_address}{address.city_address}{address.district_address}{address.detail_address}",
            'postal_code': address.postal_code,
            'carriage': shipping_fee,
            'total_price': product_total_price,
            'status': OrderStatus.PENDING_PAYMENT.value,
            'payment': total_price,
            'created_by': user_id,
            'deleted_flag' : False,
        }
        order = Order.objects.create(**order_data)
        
        order_items = [
            OrderItem(
                item_id=str(ulid.new()),
                order_id=order.order_id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                product_price=item['product_price'],
                account=item['account'],
                subtotal=item['subtotal'],
                deleted_flag=False,
                created_by=user_id,
            )
        for item in product_list
        ]
        OrderItem.objects.bulk_create(order_items)
  
    order_detail = OrderDetailSerializer(order).data
    return Response({'status': 'success','order_id': order.order_id,'message': '注文が正常に作成されました','data': order_detail}, status=200)

  
@api_view(['GET'])
def get_order_detail(request, order_id):
        logger.info("=== Starting get order detail ===")
        # 1. get order data from Order
        order = Order.objects.filter(order_id=order_id, deleted_flag=False).first()
        if not order:
            raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="注文が見つかりません",
                severity="error"
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
        if not order_items.exists():
            raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="注文項目が見つかりません",
                severity="error"
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


@api_view(['GET'])
def get_order_list(request):
        logger.info("=== Starting get order list ===")
        user_id = request.user_info.user_id
        # user_id ="Uf1e196438ad2e407c977f1ede4a39580"         # For develop
        if not user_id:
            raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="ユーザーIDが必要です",
                severity="error"
            )

        logger.info("Accessing get_order_list view")
        orders = Order.objects.filter(user_id=user_id,deleted_flag=False).order_by('-created_at')
        order_list = []

        if not orders.exists():
            return Response({"status": "success", "data": []})

        for order in orders:
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


        logger.info(f"Successfully retrieved {len(order_list)} orders")
        response = {
            "status": 200,
            "data": order_list
        }
        return Response(response, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def update_order(request, order_id):
        order = Order.objects.filter(order_id=order_id, deleted_flag=False).first()
        if not order:
            raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="注文が見つかりません",
                severity="error"
            )
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        if not serializer.is_valid():
            raise CustomAPIException(
                status=status.HTTP_400_BAD_REQUEST,
                message="無効なデータです",
                severity="error"
            )

        serializer.save()
        return Response({
            'status': 'success',
            'message': '注文が更新されました',
            'data': OrderDetailSerializer(order).data
        })


@api_view(['PATCH'])
def cancel_order(request, order_id):
    
        # 注文情報を取得
        order = Order.objects.filter(order_id=order_id, user_id=request.user_info.user_id, deleted_flag=False).first()
        if not order:
            raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="注文が見つかりません",
                severity="error"
            )
        # 注文状態は支払い待ちのみキャンセルできます
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise CustomAPIException(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message="キャンセルできません",
                severity="error"
            )

        # PayPay QRコードの処理
        if order.payment_qr_code_id:            
            # QRコードの削除をPayPayに要求
            response = delete_paypay_qr_code(order.payment_qr_code_id)

            # QRコードが存在しない場合も正常として扱う
            if response.get('resultInfo', {}).get('code') not in ['SUCCESS', 'DYNAMIC_QR_NOT_FOUND']:
                    logger.warning(f"order_id={order_id} PayPay QRコード削除失敗またはエラー発生: {response}")
            else:
                order.payment_qr_code_id = None
                logger.info(f"order_id={order_id} PayPay QRコード削除成功")

        # DBデータ更新
        order.updated_by = request.user_info.user_id
        
        # 注文状態をキャンセル(5)に更新
        order.status = OrderStatus.CANCELED.value
        order.save()
        logger.info(f"注文がキャンセルされました。order_id={order_id}")

        return Response({'status': 'success', 'message': '注文がキャンセルされました'})

@api_view(['DELETE'])
def delete_order(request, order_id):
    
        order = Order.objects.filter(order_id=order_id, user_id=request.user_info.user_id, deleted_flag=False).first()
        order.deleted_flag = True
        order.save()
        return Response({'status': 'success', 'message': '注文削除が成功しました'})

@api_view(['POST'])
def preview_order(request):
    logger.info("=== Starting get preview order ===")

    request_product_list = request.data.get('product_list', None)

    user_id = request.user_info.user_id
    
    product_list, product_total_price = validate_and_prepare_products(request_product_list, user_id)

    # todo 配送料の計算 (固定値を設定)
    shippingFee = 100
    total_price = product_total_price + shippingFee

    data = {
        "product_total_price": product_total_price,
        "shipping_fee": shippingFee,
        "total_price": total_price
    }

    response = {"status": "success", "message": "注文情報の事前取得が成功しました。", "data": data}
    return Response(response, status=status.HTTP_200_OK)