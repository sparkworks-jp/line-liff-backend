from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderUpdateSerializer
from datetime import datetime

class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(created_at=datetime.now(), updated_at=datetime.now())
            return Response(OrderCreateSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        return Response(OrderCreateSerializer(order).data)

    def put(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_at=datetime.now())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class OrderListView(APIView):
    def get(self, request):
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

        return Response(order_list, status=status.HTTP_200_OK)