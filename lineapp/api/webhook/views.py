import logging

from django.db import transaction
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

    if order_info is None:
        logger.error(f"Order error! The order with successful payment does not exist. payment_id:{merchant_order_id}")
        logger.error(f"PayPay webhook request data:{request_data}")
        return Response({"message": "OK"}, status=status.HTTP_200_OK)

    # 重複処理の防止: すでに処理済みの注文はスキップ
    if order_info.status == OrderStatus.PAID:
        logger.info(f"Webhook already processed for order_id:{order_info.order_id}, payment_id:{merchant_order_id} Skipping processing.")
        return Response({"message": "OK"}, status=status.HTTP_200_OK)

    try:
        with transaction.atomic():
            if state == 'COMPLETED':
                if str(order_info.payment) == order_amount and order_info.status == OrderStatus.PENDING_PAYMENT:
                    # Update the order status to PAID
                    order_info.status = OrderStatus.PAID
                    order_info.payment_date = paid_at
                    order_info.save()

                    logger.info(f"Order {merchant_order_id} successfully updated to PAID.")
                    return Response({"message": "OK"}, status=status.HTTP_200_OK)

                elif str(order_info.payment) != order_amount:
                    # 支払い通知にエラーが発生した場合、管理者にSlackやその他の通知手段でアラートを送信します。
                    logger.error(
                        f"Incorrect payment amount for order_id:{order_info.order_id}, payment_id:{order_info.payment_id}")
                    return Response({"message": "OK"}, status=status.HTTP_200_OK)

                elif order_info.status != OrderStatus.PENDING_PAYMENT:
                    # 支払い通知にエラーが発生した場合、管理者にSlackやその他の通知手段でアラートを送信します。
                    logger.error(
                        f"Order status error! order_id:{order_info.order_id}, order_status:{order_info.status}, payment_id:{order_info.payment_id}")
                    return Response({"message": "OK"}, status=status.HTTP_200_OK)

            logger.error(f"Unexpected state or order issue for order_id:{order_info.order_id}, state:{state}")
            return Response({"message": "OK"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error processing payment webhook for order_id:{merchant_order_id}. Exception: {str(e)}")
        return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)