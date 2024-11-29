import logging
from rest_framework.decorators import api_view

from api.order.models import Order
from rest_framework import status
from rest_framework.response import Response

from common.constants import OrderStatus
from common.ip_check import ip_whitelist_required

logger = logging.getLogger(__name__)

# 支払いステータスのコールバックについて、公式ドキュメントには署名検証機能が記載されていません。公式では、PayPayのIPアドレスをホワイトリストに登録することを推奨しています。そのため、IPホワイトリストによる検証を採用します。
# ✳開発環境と本番環境ではIPホワイトリストが異なります。
# IPアドレスをホワイトリストに登録する理由：https://www.paypay.ne.jp/opa/doc/v1.0/dynamicqrcode#tag/Webhook-Setup
# ホワイトリストの参考URL：https://integration.paypay.ne.jp/hc/en-us/articles/4414062832143-Please-provide-the-IP-address-of-Webhook-notification-source-server
@api_view(['POST'])
@ip_whitelist_required
def payment_status_webhook(request):
    logger.info("----------------payment_status_webhook-------------------")

    merchant_order_id = request.data.get('merchant_order_id', None)
    order_amount = request.data.get('order_amount', None)
    state = request.data.get('state', None)
    paid_at = request.data.get('paid_at', None)

    request_data = request.data

    logger.info(f"X-Forwarded-For: {request.headers.get('X-Forwarded-For')}")
    logger.info(
        f"payment_status_webhook: merchant_order_id={merchant_order_id}, order_amount={order_amount}, state={state}, paid_at={paid_at}")

    if not merchant_order_id or not state:
        response = {
            "status": "error",
            "message": "Invalid data",
            "errors": [{
                "code": 400,
                "message": "Invalid data"
            }],
            "data": {}
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    order_info = Order.objects.filter(payment_id=merchant_order_id).first()

    if state == 'COMPLETED' and str(
            order_info.payment) == order_amount and order_info.status == OrderStatus.PENDING_PAYMENT:

        Order.objects.filter(payment_id=merchant_order_id).update(status=OrderStatus.PAID, payment_date=paid_at)

        response = {
            "status": "success",
            "message": "OK",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_200_OK)

    elif state == 'COMPLETED' and str(order_info.payment) != order_amount:

        # 支払い通知にエラーが発生した場合、管理者にSlackやその他の通知手段でアラートを送信します。
        logger.error(
            f"The payment amount for the order is incorrect! order_id:{order_info.order_id}, payment_id:{order_info.payment_id}")

        response = {
            "status": "success",
            "message": "OK",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_200_OK)

    elif state == 'COMPLETED' and order_info.status != OrderStatus.PENDING_PAYMENT:

        # 支払い通知にエラーが発生した場合、管理者にSlackやその他の通知手段でアラートを送信します。
        logger.error(
            f"注文ステータスエラー! order_id:{order_info.order_id}, order_status:{order_info.status}, payment_id:{order_info.payment_id}")

        response = {
            "status": "success",
            "message": "OK",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_200_OK)

    elif state == 'COMPLETED' and order_info is None:
        # 支払い通知にエラーが発生した場合、管理者にSlackやその他の通知手段でアラートを送信します。
        logger.error(f"Order error! The order with successful payment does not exist. payment_id:{merchant_order_id}")
        logger.error(f"PayPay webhook request data:{request_data}")
        response = {
            "status": "success",
            "message": "OK",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_200_OK)

    else:
        # 支払い通知にエラーが発生した場合、管理者にSlackやその他の通知手段でアラートを送信します。
        if order_info is not None:
            logger.error(f"Order payment error! order_id:{order_info.order_id}, order_status:{order_info.status}, payment_id:{order_info.payment_id}")
        else:
            logger.error(f"The order does not exist. payment_id:{merchant_order_id}")
        logger.error(f"PayPay webhook request data:{request_data}")
        response = {
            "status": "success",
            "message": "OK",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_200_OK)
