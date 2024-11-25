from rest_framework import serializers
import ulid
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'item_id', 'order_id', 'product_id', 'product_name', 'product_price',
            'account', 'subtotal', 'created_by'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    payment_qr_code_id = serializers.CharField(allow_null=True, required=False)

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order_id=order.order_id, **item_data)
        
        return order

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'status', 
            'total_price', 
            'tracking_number', 
            'shipment_date', 
            'payment_date', 
            'payment',
            'updated_by'
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id', 'status', 'total_price', 'payment', 
            'order_date', 'created_at', 'updated_at'
        ]