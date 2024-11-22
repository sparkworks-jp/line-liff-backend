import logging
from rest_framework.decorators import api_view

from api.order.models import Order
from rest_framework import status
from rest_framework.response import Response

from common.constants import OrderStatus
from common.ip_check import ip_whitelist_required

logger = logging.getLogger(__name__)

# 支付状态回调，官方文档中没有看到回调有签名验证机制，因此采用IP白名单验证
# 白名单参考url:https://integration.paypay.ne.jp/hc/en-us/articles/4414062832143-Please-provide-the-IP-address-of-Webhook-notification-source-server
# 开发环境与生产环境IP白名单不同
# https://pxgboy2hi7zpzhyitpghh6iy4u0iyyno.lambda-url.ap-northeast-1.on.aws/payment/callback
# https://rested-conversely-seahorse.ngrok-free.app/api/webhook/payment/status

@api_view(['POST'])
@ip_whitelist_required
def payment_status_webhook(request):

    logger.info("----------------payment_status_webhook-------------------")

    merchant_order_id = request.data.get('merchant_order_id', None)
    order_amount = request.data.get('order_amount', None)
    state = request.data.get('state', None)
    paid_at = request.data.get('paid_at', None)

    logger.info(f"X-Forwarded-For: {request.headers.get('X-Forwarded-For')}")
    logger.info(f"payment_status_webhook: merchant_order_id={merchant_order_id}, order_amount={order_amount}, state={state}, paid_at={paid_at}")

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

    if state == 'COMPLETED' and order_info.payment == order_amount:

        Order.objects.filter(payment_id=merchant_order_id).update(status=OrderStatus.COMPLETED, payment_date=paid_at)

        response = {
            "status": "success",
            "message": "OK",
            "errors": [],
            "data": {}
        }

        return Response(response, status=status.HTTP_200_OK)
