import logging
import os
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import paypayopa
from rest_framework.decorators import api_view

from api.order.models import Order
from rest_framework import status
from rest_framework.response import Response

from common.constants import OrderStatus
from core.middleware.line_auth import line_auth_required

logger = logging.getLogger(__name__)

PAYPAY_API_KEY = os.getenv["PAYPAY_API_KEY"]
PAYPAY_API_SECRET = os.getenv("PAYPAY_API_SECRET")
PAYPAY_CLIENT_ID = os.getenv("PAYPAY_CLIENT_ID")
PAYPAY_MERCHANT_ID = os.getenv("PAYPAY_MERCHANT_ID")
APP_HOST_NAME = os.getenv("APP_HOST_NAME")
client = paypayopa.Client(auth=(PAYPAY_API_KEY, PAYPAY_API_SECRET),
                          production_mode=False)
client.set_assume_merchant(PAYPAY_MERCHANT_ID)

# 查询订单详细--> check 订单状态 订单为待支付状态才允许创建支付  --> 无效掉之前的支付Link --> request PayPay 获得支付Link 将id 更新到订单 payment_id --> 返回支付Link

@api_view(['POST'])
# @line_auth_required
def create_payment(request, order_id):

    logger.info("----------------create_payment-------------------")

    # Todo
    # user_id = request.user.user_id
    user_id = '01JD4G4GGWFJ6KBHNKYWT1F0T9'


    pending_payment_order_info = Order.objects.filter(user_id=user_id, order_id=order_id, deleted_flag=False, status=OrderStatus.PENDING_PAYMENT).first()

    # check 当前订单是否为未支付状态的订单
    if pending_payment_order_info is None:
        message = {
            'status': 'error',
            "message": "不存在未支付订单",
            "errors": [{
                "code": 400,
                "message": "不存在未支付订单"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    # 判断订单是否超时（24小时）
    jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
    if jst_now - pending_payment_order_info.created_at > timedelta(hours=24):
        message = {
            'status': 'error',
            "message": "订单超时，不可支付",
            "errors": [{
                "code": 400,
                "message": "订单超时，不可支付"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    # 判断之前是否已经创建过支付Link
    if pending_payment_order_info.payment_id is None:
        # 创建支付Link
        merchant_payment_id = str(uuid.uuid4())

        amount = int(pending_payment_order_info.payment)

        request = {
            "merchantPaymentId": merchant_payment_id,
            "codeType": "ORDER_QR",
            "redirectUrl": f"{APP_HOST_NAME}/order?id={order_id}",
            "redirectType": "WEB_LINK",
            "orderDescription": "order description",
            "amount": {
                "amount": amount,
                "currency": "JPY",
            },
        }

        response = client.Code.create_qr_code(request)

        if response['resultInfo']['code'] == 'SUCCESS':
            payment_link = response['data']['url']
            payment_link_response = {
                'status': 'success',
                "message": "payment_linkが正常に取得されました。",
                "errors": [],
                "data": {
                    "payment_link": payment_link
                }
            }

            return Response(payment_link_response, status=status.HTTP_200_OK)
    else:
        # 删除之前的支付Link
        print(pending_payment_order_info.payment_qr_code_id)
        print("PAYPAY_API_KEY:", os.getenv("PAYPAY_API_KEY"))
        print("PAYPAY_API_SECRET:", os.getenv("PAYPAY_API_SECRET"))
        response = client.Code.delete_qr_code(str(pending_payment_order_info.payment_qr_code_id))

        if response['resultInfo']['code'] == 'SUCCESS':
            # 创建支付Link
            merchant_payment_id = str(uuid.uuid4())

            amount = int(pending_payment_order_info.payment)

            request = {
                "merchantPaymentId": merchant_payment_id,
                "codeType": "ORDER_QR",
                "redirectUrl": f"{APP_HOST_NAME}/order?id={order_id}",
                "redirectType": "WEB_LINK",
                "orderDescription": "order description",
                "amount": {
                    "amount": amount,
                    "currency": "JPY",
                },
            }

            response = client.Code.create_qr_code(request)

            if response['resultInfo']['code'] == 'SUCCESS':
                # 更新order表
                payment_qr_code_id = response['data']['codeId']
                Order.objects.filter(order_id=order_id).update(payment_id=merchant_payment_id, payment_qr_code_id=payment_qr_code_id)
                payment_link = response['data']['url']
                payment_link_response = {
                    'status': 'success',
                    "message": "payment_linkが正常に取得されました。",
                    "errors": [],
                    "data": {
                        "payment_link": payment_link
                    }
                }

                return Response(payment_link_response, status=status.HTTP_200_OK)
