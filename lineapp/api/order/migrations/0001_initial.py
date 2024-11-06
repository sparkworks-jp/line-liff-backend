# Generated by Django 4.2.5 on 2024-11-06 06:27

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
                ('express_information', models.TextField(db_comment='配送先情報:{phone,address,name,,,,,,とか}')),
                ('carriage', models.IntegerField(blank=True, db_comment='配送料', null=True)),
                ('total_price', models.IntegerField(blank=True, db_comment='総金額', null=True)),
                ('coupon_count', models.IntegerField(blank=True, db_comment='クーポン金額:=総商品のprice', null=True)),
                ('payment', models.IntegerField(blank=True, db_comment='支払金額: =総金額＋配送料-クーポン', null=True)),
                ('status', models.IntegerField(db_comment='注文ステータス:"01作成済み"、"02支払い待ち"、"03支払い済み"、"04発送済み"、"05完了"、"06キャンセル"')),
                ('tracking_number', models.CharField(db_comment='追跡番号', max_length=50)),
                ('shipment_date', models.DateTimeField(blank=True, db_comment='発送日', null=True)),
                ('payment_date', models.DateTimeField(blank=True, db_comment='支払日', null=True)),
                ('payment_id', models.CharField(blank=True, db_comment='支払い番号:paypay\u3000支払い番号', max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_comment='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, db_comment='更新日時')),
                ('updated_by', models.CharField(blank=True, db_comment='更新者', max_length=256, null=True)),
                ('created_by', models.CharField(blank=True, db_comment='登録者', max_length=256, null=True)),
                ('deleted_flag', models.BooleanField(blank=True, db_comment='削除フラグ', null=True)),
            ],
            options={
                'db_table': 'line.orders',
                'db_table_comment': '注文',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(db_comment='注文番号', max_length=50)),
                ('product_id', models.CharField(db_comment='商品番号', max_length=50)),
                ('product_name', models.CharField(db_comment='商品名', max_length=255)),
                ('product_price', models.IntegerField(db_comment='商品価格')),
                ('product_size_information', models.IntegerField(blank=True, db_comment='商品サイズ情報:（json数组-重量，体积，规格等）_具体待定', null=True)),
                ('product_store_barcode', models.CharField(blank=True, db_comment='倉庫バーコード', max_length=100, null=True)),
                ('discount_rate', models.DecimalField(blank=True, db_comment='割引率', decimal_places=2, max_digits=10, null=True)),
                ('discount_amount', models.IntegerField(blank=True, db_comment='割引金額', null=True)),
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
                'db_table': 'line.order_items',
                'db_table_comment': '注文アイテム',
            },
        ),
    ]
