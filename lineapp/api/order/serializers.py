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


class OrderItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['item_id', 'product_id', 'product_name', 'product_price', 'account', 'subtotal']
    
    def to_representation(self, instance):
        return {
            'id': instance.product_id,
            'name': instance.product_name,
            'quantity': instance.account,
            'price': instance.product_price,
            'image': instance.product_id
        }


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'orderId': instance.order_id,
            'trackingNumber': instance.tracking_number,
            'orderStatus': str(instance.status).zfill(2),
            'items': data['items'],
            'totalAmount': instance.total_price,
            'discount': instance.discount_amount,
            'finalAmount': instance.payment,
            'deliveryFee': instance.carriage,
            'orderDate': instance.order_date.strftime('%Y-%m-%d') if instance.order_date else None,
            'estimatedDelivery': instance.estimated_delivery_date.strftime('%Y-%m-%d') if instance.estimated_delivery_date else None,
            'postalCode': instance.postal_code,
            'address': instance.address
        }
