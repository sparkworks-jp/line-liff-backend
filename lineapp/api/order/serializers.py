from rest_framework import serializers
import ulid
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id', 
            'status',
            'status_display',  
            'total_price', 
            'payment', 
            'order_date', 
            'created_at', 
            'updated_at',
            'items'
        ]

    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order_id=obj.order_id)
        return OrderItemSerializer(order_items, many=True).data

    def get_status_display(self, obj):
        STATUS_CHOICES = {
            1: "支払い待ち",
            2: "支払い済み",
            3: "発送済み",
            4: "完了",
            5: "キャンセル"
        }
        return STATUS_CHOICES.get(obj.status, "不明")
    
