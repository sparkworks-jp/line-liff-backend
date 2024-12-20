# Generated by Django 4.2.5 on 2024-11-19 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.CharField(db_comment='注文番号', max_length=50, primary_key=True, serialize=False)),
                ('user_id', models.CharField(db_comment='ユーザーID', max_length=50)),
                ('order_date', models.DateTimeField(db_comment='注文作成日')),
                ('carriage', models.IntegerField(blank=True, db_comment='配送料', null=True)),
                ('total_price', models.IntegerField(blank=True, db_comment='総金額', null=True)),
                ('coupon_count', models.IntegerField(blank=True, db_comment='クーポン金額', null=True)),
                ('payment', models.IntegerField(blank=True, db_comment='支払金額', null=True)),
                ('status', models.IntegerField(db_comment='注文ステータス')),
                ('tracking_number', models.CharField(db_comment='追跡番号', max_length=50)),
                ('shipment_date', models.DateTimeField(blank=True, db_comment='発送日', null=True)),
                ('payment_date', models.DateTimeField(blank=True, db_comment='支払日', null=True)),
                ('payment_qr_code_id', models.CharField(db_comment='支払い検証クラスID', max_length=50)),
                ('payment_id', models.CharField(blank=True, db_comment='支払い番号', max_length=10, null=True)),
                ('created_at', models.DateTimeField(db_comment='作成日時')),
                ('updated_at', models.DateTimeField(db_comment='更新日時')),
                ('updated_by', models.CharField(blank=True, db_comment='更新者', max_length=256, null=True)),
                ('created_by', models.CharField(blank=True, db_comment='登録者', max_length=256, null=True)),
                ('deleted_flag', models.BooleanField(blank=True, db_comment='削除フラグ', null=True)),
                ('address', models.TextField(blank=True, db_comment='住所', null=True)),
                ('name_katakana', models.CharField(blank=True, db_comment='名前カタカナ', max_length=256, null=True)),
                ('name', models.CharField(blank=True, db_comment='名前', max_length=256, null=True)),
                ('phone_number', models.CharField(blank=True, db_comment='電話番号', max_length=50, null=True)),
                ('postal_code', models.CharField(blank=True, db_comment='郵便番号', max_length=50, null=True)),
                ('coupon_id', models.CharField(blank=True, db_comment='クーポンID', max_length=256, null=True)),
                ('discount_amount', models.DecimalField(blank=True, db_comment='割引額',  default=0, max_digits=10, null=True)),
            ],
            options={
                'db_table': 'orders',
                'db_table_comment': '注文',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('item_id', models.CharField(auto_created=True, primary_key=True, serialize=False,max_length=50)),
                ('order_id', models.CharField(db_comment='注文番号', max_length=50)),
                ('product_id', models.CharField(db_comment='商品番号', max_length=50)),
                ('product_name', models.CharField(db_comment='商品名', max_length=255)),
                ('product_price', models.IntegerField(db_comment='商品価格')),
                ('product_size_information', models.TextField(blank=True, db_comment='商品サイズ情報:（json数组-重量，体积，规格等）_具体待定', null=True)),
                ('product_store_barcode', models.CharField(blank=True, db_comment='倉庫バーコード', max_length=100, null=True)),
                ('account', models.IntegerField(db_comment='購入数量')),
                ('subtotal', models.IntegerField(db_comment='小計金額')),
                ('remark', models.TextField(blank=True, db_comment='顧客の商品の備考', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_comment='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, db_comment='更新日時')),
                ('updated_by', models.CharField(blank=True, db_comment='更新者', max_length=256, null=True)),
                ('created_by', models.CharField(blank=True, db_comment='登録者', max_length=256, null=True)),
                ('deleted_flag', models.BooleanField(blank=True, db_comment='削除フラグ', null=True)),
            ],
            options={
                'db_table': 'order_items',
                'db_table_comment': '注文アイテム',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('coupon_id', models.CharField(primary_key=True, max_length=256)),
                ('coupon_code', models.CharField(unique=True, max_length=20)),
                ('coupon_name', models.CharField(max_length=256)),
                ('discount_type', models.SmallIntegerField()),
                ('discount_value', models.DecimalField(max_digits=10)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('min_order_amount', models.DecimalField(max_digits=10,  null=True, blank=True)),
                ('max_discount_amount', models.DecimalField(max_digits=10,  null=True, blank=True)),
                ('usage_count', models.IntegerField(default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_by', models.CharField(max_length=256, null=True, blank=True)),
                ('deleted_flag', models.BooleanField(default=False, null=True)),
                ('product_id', models.CharField(max_length=256, null=True, blank=True)),
            ],
            options={
                'db_table': 'coupons',
                'db_table_comment': 'クーポン管理テーブル',
            },
        )
        
    ]
