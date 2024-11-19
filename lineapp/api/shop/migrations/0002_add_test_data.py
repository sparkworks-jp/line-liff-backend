from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL([
            """
            INSERT INTO products (
                product_id, product_name, description, product_price, 
                product_marque, product_store_barcode, product_size_information, 
                sale_status, created_at, updated_at
            ) VALUES
            ('PROD001', 'らせん酥（螺旋酥）', 'A tasty spiral pastry', 340, 
             'SNACK001', 'BAR123456', 'Weight: 100g', 1, NOW(), NOW()),
            ('PROD003', 'たんこう酥（蛋黄酥）', 'Egg yolk pastry', 500, 
             'SNACK002', 'BAR654321', 'Weight: 120g', 1, NOW(), NOW())
            """
        ],
        reverse_sql=[
            "DELETE FROM products"
        ])
    ]