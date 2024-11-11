from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timezone
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderUpdateSerializer

@api_view(['POST'])
def create_order(request):
    serializer = OrderCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    serializer = OrderCreateSerializer(order)
    return Response(serializer.data)


@api_view(['GET'])
def get_order_list(request):
    orders = Order.objects.all()
    order_list = []

    for order in orders:
        items = OrderItem.objects.filter(order_id=order.order_id)
        items_summary = ', '.join([f"{item.product_name} x{item.account}" for item in items])
        
        order_data = {
            "id": order.order_id,
            "date": order.order_date.strftime("%Y-%m-%d"),
            "items": items_summary,
            "total": f"¥{order.total_price:,.0f}"
        }
        order_list.append(order_data)

    return JsonResponse(order_list, safe=False)


@api_view(['PUT'])
def update_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(updated_at=datetime.now(timezone.utc))
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.delete()
    return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)