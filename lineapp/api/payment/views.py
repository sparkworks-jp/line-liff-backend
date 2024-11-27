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
PAYMENT_TIMEOUT_HOURS = 24
TIMEZONE = "Asia/Tokyo"
PAYPAY_API_KEY = os.getenv("PAYPAY_API_KEY")
PAYPAY_API_SECRET = os.getenv("PAYPAY_API_SECRET")
PAYPAY_CLIENT_ID = os.getenv("PAYPAY_CLIENT_ID")
PAYPAY_MERCHANT_ID = os.getenv("PAYPAY_MERCHANT_ID")
APP_HOST_NAME = os.getenv("APP_HOST_NAME")
client = paypayopa.Client(auth=(PAYPAY_API_KEY, PAYPAY_API_SECRET),
                          production_mode=False)
client.set_assume_merchant(PAYPAY_MERCHANT_ID)

# 注文の詳細を確認 --> 注文状態を確認 (未支払い状態のみ支払いリンクを作成可能) --> 以前の支払いリンクを無効化 --> PayPayに支払いリンクをリクエスト --> 支払いリンクIDを注文に更新 --> 支払いリンクを返す

@api_view(['POST'])
# @line_auth_required
def create_payment(request, order_id):

    logger.info("----------------create_payment-------------------")

    # Todo
    # user_id = request.user.user_id
    # user_id = '01JD4G4GGWFJ6KBHNKYWT1F0T9'
    user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    # 未支払い状態の注文を取得
    pending_payment_order_info = Order.objects.filter(
        user_id=user_id,
        order_id=order_id,
        deleted_flag=False,
        status__in=[OrderStatus.CREATED, OrderStatus.PENDING_PAYMENT]  
    ).first()
    # 未支払い状態の注文が存在しない場合
    if pending_payment_order_info is None:
        message = {
            'status': 'error',
            "message": "未支払いの注文が存在しません。",
            "errors": [{
                "code": 400,
                "message": "未支払いの注文が存在しません。"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    # 注文が24時間を超えていないか確認
    jst_now = datetime.now(ZoneInfo(TIMEZONE))
    if jst_now - pending_payment_order_info.created_at > timedelta(PAYMENT_TIMEOUT_HOURS):
        message = {
            'status': 'error',
            "message": "注文がタイムアウトしました。支払いはできません。",
            "errors": [{
                "code": 400,
                "message": "注文がタイムアウトしました。支払いはできません。"
            }],
            "data": {}
        }
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"支払いリンクの作成を開始します。order_id={order_id}, user_id={user_id}")

    try:

        # 以前に支払いリンクが作成されていない場合
        if pending_payment_order_info.payment_id is None:
            # 支払いリンクを作成
            amount = int(pending_payment_order_info.payment)
            response, merchant_payment_id = create_paypay_qr_code(order_id, amount)

            if response['resultInfo']['code'] == 'SUCCESS':
                payment_link = response['data']['url']
                payment_link_response = {
                    'status': 'success',
                    "message": "支払いリンクが正常に取得されました。",
                    "errors": [],
                    "data": {
                        "payment_link": payment_link
                    }
                }

                payment_qr_code_id = response['data']['codeId']
                Order.objects.filter(order_id=order_id).update(payment_id=merchant_payment_id, payment_qr_code_id=payment_qr_code_id)

                return Response(payment_link_response, status=status.HTTP_200_OK)
        else:
            # 以前の支払いリンクを削除
            response = delete_paypay_qr_code(pending_payment_order_info.payment_qr_code_id)

            if response['resultInfo']['code'] == 'SUCCESS' or response['resultInfo']['code'] == 'DYNAMIC_QR_NOT_FOUND':
                # 新たな支払いリンクを作成
                amount = int(pending_payment_order_info.payment)
                response, merchant_payment_id = create_paypay_qr_code(order_id, amount)

                if response['resultInfo']['code'] == 'SUCCESS':
                    # 注文テーブルを更新
                    payment_qr_code_id = response['data']['codeId']
                    Order.objects.filter(order_id=order_id).update(payment_id=merchant_payment_id, payment_qr_code_id=payment_qr_code_id)
                    payment_link = response['data']['url']
                    payment_link_response = {
                        'status': 'success',
                        "message": "支払いリンクが正常に取得されました。",
                        "errors": [],
                        "data": {
                            "payment_link": payment_link
                        }
                    }

                    return Response(payment_link_response, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"支払いリンク作成中に例外が発生しました。order_id={order_id}, error={str(e)}")

        response = {
            'status': 'error',
            "message": "システムエラーが発生しました。",
            "errors": [{
                "code": 500,
                "message": "予期しないエラーが発生しました。"
            }],
            "data": {
                "payment_link": payment_link
            }
        }
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_paypay_qr_code(order_id, amount):
    try:

        merchant_payment_id = str(uuid.uuid4())
        request = {
            "merchantPaymentId": merchant_payment_id,
            "codeType": "ORDER_QR",
            "redirectUrl": f"{APP_HOST_NAME}/paymentcomplete",
            "redirectType": "WEB_LINK",
            "orderDescription": "注文の説明",
            "amount": {
                "amount": amount,
                "currency": "JPY",
            },
        }
        response = client.Code.create_qr_code(request)
        return response, merchant_payment_id
    except Exception as e:
        logger.error(f"QRコード作成中に例外が発生しました。order_id={order_id}, error={str(e)}")
        raise


def delete_paypay_qr_code(qr_code_id):
    try:
        response = client.Code.delete_qr_code(str(qr_code_id))
        print("delete_paypay_qr_code",response)
        return response
    except Exception as e:
        logger.error(f"QRコード削除中に例外が発生しました。qr_code_id={qr_code_id}, error={str(e)}")
        raise

