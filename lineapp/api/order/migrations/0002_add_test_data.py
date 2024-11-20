# api/order/migrations/0002_add_test_data.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('order', '0001_initial'),
        ('user', '0002_add_test_data'),
        ('shop', '0002_add_test_data'),
    ]

    operations = [
        migrations.RunSQL([
            # 插入订单数据
            """
            INSERT INTO orders (
                order_id, user_id, order_date,  carriage, 
                total_price, coupon_count, payment, status, tracking_number, 
                shipment_date, payment_date, payment_id, created_at, updated_at
            ) VALUES
            ('ORD12345678', 'USER001', '2023-05-01',  1870,
             2970, 100, 2870, 1, 'TRK98765432', '2023-05-02', '2023-05-01', 
             'PAY12345', NOW(), NOW())
            """,
            
            # 插入订单项数据
            """
            INSERT INTO order_items (
                order_id, product_id, product_name, product_price, 
                product_size_information, product_store_barcode, discount_rate, 
                discount_amount, account, subtotal, remark, created_at, updated_at
            ) VALUES
            ('ORD12345678', 'PROD001', 'らせん酥（螺旋酥）', 340, NULL,
             'BAR123456', 0.1, 34, 2, 680, 'Delicious snack', NOW(), NOW()),
            ('ORD12345678', 'PROD003', 'たんこう酥（蛋黄酥）', 500, NULL,
             'BAR654321', 0.05, 25, 3, 1500, 'Great for sharing', NOW(), NOW())
            """
        ],
        reverse_sql=[
            "DELETE FROM order_items",
            "DELETE FROM orders"
        ])
    ]