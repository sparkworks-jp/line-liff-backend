from rest_framework import serializers,status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction

from common.constants import SaleStatus, OrderStatus, shipping_fees
from common.exceptions import CustomAPIException
from common.util import join_with_space, join_without_space, format_currency, format_date, format_datetime, summarize_items
from .models import Order, OrderItem
from ..shop.models import Product
from ..user.models import UserAddress
from ..payment.views import delete_paypay_qr_code
from .serializers import ( OrderDetailSerializer)

import ulid
import logging


logger = logging.getLogger(__name__)



# check ページの支払いボタンには注文情報が保存され、注文ステータスは未払いです。
@api_view(['POST'])
def create_order(request):
    logger.info("=== Starting order creation ===")

    user_id = request.user_info.user_id
    # user_id ="Uf1e196438ad2e407c977f1ede4a39580" //for develop

    request_product_list = request.data.get('product_list', None)
    
    product_list, product_total_price = validate_and_prepare_products(request_product_list, user_id)
    
    address = UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).first()
    
    shipping_fee = calculate_shipping_fee(address.prefecture_address)
    
    total_price = product_total_price + shipping_fee


    # DBデータ更新
    with transaction.atomic():

        order_data = {
            'order_id': str(ulid.new()),
            'user_id': user_id,
            'order_date': timezone.now(),
            'name': join_with_space(address.last_name,address.first_name),
            'name_katakana': join_with_space(address.last_name_katakana, address.first_name_katakana),
            'phone_number': address.phone_number,
            'address': join_without_space(address.prefecture_address,address.city_address, address.district_address, address.detail_address),
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
    user_id = request.user_info.user_id

    # get order data from Order
    order = Order.objects.filter(order_id=order_id, user_id = user_id, deleted_flag=False).first()
    if not order:
        raise CustomAPIException(
            status=status.HTTP_404_NOT_FOUND,
            message="注文が見つかりません",
            severity="error"
        )
    # get order items data from OrderItem
    order_items = OrderItem.objects.filter(order_id=order_id, deleted_flag=False).values('product_id','product_name', 'account', 'product_price')
    if not order_items.exists():
            raise CustomAPIException(
                status=status.HTTP_404_NOT_FOUND,
                message="注文項目が見つかりません",
                severity="error"
            )
    
    # get product pics
    product_ids = [item['product_id'] for item in order_items]
    products = {p['product_id']: p['image'] for p in Product.objects.filter(product_id__in=product_ids).values('product_id', 'image')}

    # items data準備
    items_data = []
    for item in order_items:
        items_data.append({
            'id': item['product_id'],
            'name': item['product_name'],
            'quantity': item['account'],
            'price': item['product_price'],
            'image': products.get(item['product_id'])
        })

    # レスポンスデータ準備
    data = {
        'orderId': order.order_id,
        'trackingNumber': order.tracking_number,
        'orderStatus': order.status,
        'items': items_data,
        'totalAmount': format_currency(order.total_price),
        'discount': format_currency(order.discount_amount),
        'finalAmount': format_currency(order.payment),
        'deliveryFee': format_currency(order.carriage),
        'orderDate': format_date(order.order_date),
        'estimatedDelivery': format_date(order.estimated_delivery_date),
        'postalCode': order.postal_code,
        'address': order.address,
    }

    return Response({'status': 'success', 'data': data})


@api_view(['GET'])
def get_order_list(request):

    logger.info("=== Starting get order list ===")
    user_id = request.user_info.user_id
    # user_id ="Uf1e196438ad2e407c977f1ede4a39580"         # For develop

    orders = Order.objects.filter(user_id=user_id,deleted_flag=False).order_by('-created_at')
    if not orders.exists():
        raise CustomAPIException(
            status=status.HTTP_404_NOT_FOUND,
            message="注文が見つかりません",
            severity="error"
        )

    order_list = []
    for order in orders:
        items = OrderItem.objects.filter(order_id=order.order_id ,deleted_flag=False)
        items_summary = summarize_items(items)
        order_data = {
            "id": order.order_id,
            "date": order.order_date.strftime("%Y-%m-%d"),
            "items": items_summary,
            "total": format_currency(order.payment),
            "status": order.status,
            "created_at": format_datetime(order.created_at)
        }
        order_list.append(order_data)

    logger.info(f"Successfully retrieved {len(order_list)} orders")
    response = {"status": 200, "data": order_list}

    return Response(response, status=status.HTTP_200_OK)



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

    address = UserAddress.objects.filter(user_id=user_id, deleted_flag=False, is_default=True).first()
    if address is None:
        data = {
                "product_total_price": product_total_price,
                "shipping_fee": 0,
                "total_price": product_total_price
            }

        response = {"status": "success", "message": "注文情報の事前取得が成功しました。", "data": data}
        return Response(response, status=status.HTTP_200_OK)
  
    shipping_fee = calculate_shipping_fee(address.prefecture_address)

    total_price = product_total_price + shipping_fee

    data = {
        "product_total_price": product_total_price,
        "shipping_fee": shipping_fee,
        "total_price": total_price
    }

    response = {"status": "success", "message": "注文情報の事前取得が成功しました。", "data": data}
    return Response(response, status=status.HTTP_200_OK)


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


def calculate_shipping_fee(prefecture_id):
    shipping_fee = shipping_fees.get(prefecture_id)
    return shipping_fee