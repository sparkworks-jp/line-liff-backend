import json
import logging
import os

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


# Client.__init__() got an unexpected keyword argument 'proxies'
# openai 与 httpx 版本不匹配，与httpx 2.8.0冲突，httpx降级0.27.2，或者升级openai 1.55.3，openai此版本修复了该问题

import openai
openai.api_key = os.environ.get("OPEN_AI_API_KEY")
@api_view(['POST'])
def openai_function_test(request):
    question = request.data.get('question', None)
    logger.info(f"Received question: {question}")

    user_id = '01JD4G4GGWFJ6KBHNKYWT1F0T9'

    if not question:
        return Response({"error": "Question is required."}, status=400)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. If you use function call, the Function arguments must be in English."},
                {"role": "user", "content": question},
            ],
            tools=tools,
        )

        print(response)

        # message = response['choices'][0]['message']
        message = response.choices[0].message
        print(message)
        if message.tool_calls:
            # function_name = message['tool_calls'][0]['function']['name']
            # arguments = message['tool_calls'][0]['function']['arguments']
            function_name = message.tool_calls[0].function.name
            arguments = message.tool_calls[0].function.arguments
            arguments_dict = eval(arguments)

            if function_name == "get_weather":
                city = arguments_dict.get("city")
                weather = get_weather(city)

                logger.info(f'weather: {weather}')
                logger.info(f'city: {city}')

                if weather:
                    user_friendly_response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Please answer the user's questions in Japanese using the following content as a reference. Please answer based on the content."},
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": f"The weather in {city} is {weather}. This is the accurate and final answer."}
                        ]
                    )
                    final_answer = user_friendly_response.choices[0].message.content
                    return Response({"answer": final_answer}, status=200)


            elif function_name == "get_order_info":

                info = get_order_info(user_id)

                user_friendly_response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system",
                         "content": "You are a helpful assistant. Please answer the user's questions in Japanese using the following content as a reference. Please answer based on the content."},
                        {"role": "user", "content": question},
                        {"role": "assistant",
                         "content": f"content: {info}. This is the accurate and final answer."}
                    ]
                )
                print(user_friendly_response)
                final_answer = user_friendly_response.choices[0].message.content
                return Response({"answer": final_answer}, status=200)




        else:
            answer = message['content']
            return Response({"answer": answer}, status=200)

    except Exception as e:
        logger.error(f"Error during OpenAI request: {e}")
        return Response({"error": str(e)}, status=500)



def get_weather(city):
    weather_data = {
        "Tokyo": "Sunny, 25°C",
        "Osaka": "Cloudy, 22°C",
        "Kyoto": "Rainy, 18°C"
    }
    return weather_data.get(city, "City not found")


def get_order_info(user_id):
    sql = """
        select *
        from orders
        left join order_items
            on orders.order_id = order_items.order_id
        where orders.user_id = %(user_id)s
            and orders.deleted_flag = False
    """

    order_list = Order.objects.raw(sql, {"user_id": user_id})

    order_dict = {}

    for order in order_list:
        if order.order_id not in order_dict:
            order_dict[order.order_id] = {
                'order_id': order.order_id,
                'user_id': order.user_id,
                'coupon_id': order.coupon_id,
                'discount_amount': order.discount_amount,
                'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S') if order.order_date else None,
                'carriage': order.carriage,
                'total_price': order.total_price,
                'coupon_count': order.coupon_count,
                'payment': order.payment,
                'status': order.status,
                'tracking_number': order.tracking_number,
                'shipment_date': order.shipment_date.strftime('%Y-%m-%d %H:%M:%S') if order.shipment_date else None,
                'payment_date': order.payment_date.strftime('%Y-%m-%d %H:%M:%S') if order.payment_date else None,
                'payment_qr_code_id': order.payment_qr_code_id,
                'payment_id': order.payment_id,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None,
                'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else None,
                'address': order.address,
                'name_katakana': order.name_katakana,
                'name': order.name,
                'phone_number': order.phone_number,
                'postal_code': order.postal_code,
                'estimated_delivery_date': order.estimated_delivery_date.strftime('%Y-%m-%d %H:%M:%S') if order.estimated_delivery_date else None,
                'order_items': []  # 初始化订单项列表
            }


        if order.item_id:
            order_item = {
                'item_id': order.item_id,
                'product_id': order.product_id,
                'product_name': order.product_name,
                'product_price': order.product_price,
                'product_size_information': order.product_size_information,
                'product_store_barcode': order.product_store_barcode
            }
            order_dict[order.order_id]['order_items'].append(order_item)

    formatted_order_list = list(order_dict.values())

    if not formatted_order_list:
        return json.dumps({"message": "Order not found"})

    return json.dumps({"orders": formatted_order_list})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city",
                    },
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_info",
            "description": "Retrieve detailed information about a specific order, including the order ID, customer details, items ordered, total cost, status, and delivery information. This function helps in tracking the order's progress and providing relevant updates to both the customer .",
        }
    }

]

