import logging
import os
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone

from common.exceptions import CustomAPIException
import paypayopa
from rest_framework.decorators import api_view
from api.order.models import Order
from rest_framework import status
from rest_framework.response import Response
from common.constants import OrderStatus

logger = logging.getLogger(__name__)
PAYMENT_TIMEOUT_HOURS = int(os.getenv('PAYMENT_TIMEOUT_HOURS', '24'))
TIMEZONE = os.getenv("TIMEZONE")
PAYPAY_API_KEY = os.getenv("PAYPAY_API_KEY")
PAYPAY_API_SECRET = os.getenv("PAYPAY_API_SECRET")
PAYPAY_CLIENT_ID = os.getenv("PAYPAY_CLIENT_ID")
PAYPAY_MERCHANT_ID = os.getenv("PAYPAY_MERCHANT_ID")
APP_HOST_NAME = os.getenv("APP_HOST_NAME")
client = paypayopa.Client(auth=(PAYPAY_API_KEY, PAYPAY_API_SECRET),
                          production_mode=os.getenv("IS_PRODUCTION_MODE") == "True")
client.set_assume_merchant(PAYPAY_MERCHANT_ID)

# 注文の詳細を確認 --> 注文状態を確認 (未支払い状態のみ支払いリンクを作成可能) --> 以前の支払いリンクを無効化 --> PayPayに支払いリンクをリクエスト --> 支払いリンクIDを注文に更新 --> 支払いリンクを返す

@api_view(['POST'])
  
def create_payment(request, order_id):

    logger.info("----------------create_payment-------------------")

    # Todo
    user_id = request.user_info.user_id
    # user_id = 'Uf1e196438ad2e407c977f1ede4a39580'

    # 未支払い状態の注文を取得
    pending_payment_order_info = Order.objects.filter(
        user_id=user_id,
        order_id=order_id,
        deleted_flag=False,
        status=OrderStatus.PENDING_PAYMENT
    ).first()
    # 未支払い状態の注文が存在しない場合
    if pending_payment_order_info is None:
        raise CustomAPIException(
            status=status.HTTP_404_NOT_FOUND,
            message="未支払いの注文が存在しません。",
            severity="error"
        )

    # 注文が24時間を超えていないか確認
    jst_now = timezone.now()
    if jst_now - pending_payment_order_info.created_at > timedelta(PAYMENT_TIMEOUT_HOURS):
        raise CustomAPIException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="注文がタイムアウトしました。支払いはできません。",
            severity="error"
        )

    logger.info(f"支払いリンクの作成を開始します。order_id={order_id}, user_id={user_id}")
    try:

            # 以前に支払いリンクが作成されていない場合
            if pending_payment_order_info.payment_id is not None:
            # 以前の支払いリンクを削除
                response = delete_paypay_qr_code(pending_payment_order_info.payment_qr_code_id)
                if not (response['resultInfo']['code'] == 'SUCCESS' or response['resultInfo']['code'] == 'DYNAMIC_QR_NOT_FOUND'):
                    raise CustomAPIException(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        message="既存の支払いリンクの削除に失敗しました。",
                        severity="error"
                    )
            # 支払いリンクを作成
            amount = int(pending_payment_order_info.payment)
            response, merchant_payment_id = create_paypay_qr_code(order_id, amount)

            if response['resultInfo']['code'] == 'SUCCESS':
                payment_link = response['data']['url']
                logger.info(f"新規支払いリンク生成: {payment_link}")
                logger.info(f"支払いQRコードID: {response['data']['codeId']}")
                logger.info(f"Merchant Payment ID: {merchant_payment_id}")
                payment_link_response = {
                    'status': 'success',
                    "message": "支払いリンクが正常に取得されました。",
                    "data": {
                        "payment_link": payment_link
                    }
                }

                payment_qr_code_id = response['data']['codeId']
                Order.objects.filter(order_id=order_id).update(payment_id=merchant_payment_id, payment_qr_code_id=payment_qr_code_id)

                return Response(payment_link_response, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"支払いリンク作成中に例外が発生しました。order_id={order_id}, error={str(e)}")
        raise CustomAPIException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="システムエラーが発生しました。",
            severity="error"
        )


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
        return response
    except Exception as e:
        logger.error(f"QRコード削除中に例外が発生しました。qr_code_id={qr_code_id}, error={str(e)}")
        raise

