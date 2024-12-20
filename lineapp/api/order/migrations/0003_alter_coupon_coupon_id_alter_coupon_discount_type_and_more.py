# Generated by Django 4.2.5 on 2024-11-22 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_add_test_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='coupon_id',
            field=models.CharField(max_length=256, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount_type',
            field=models.SmallIntegerField(choices=[(1, '定額割引'), (2, 'パーセント割引')]),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount_value',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='max_discount_amount',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='min_order_amount',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.TextField(blank=True, db_comment='配送先住所', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='coupon_count',
            field=models.IntegerField(blank=True, db_comment='クーポン金額:=総商品のprice', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='coupon_id',
            field=models.CharField(blank=True, db_comment='クーポンID', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_comment='作成日時'),
        ),
        migrations.AlterField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(blank=True, db_comment='割引額', decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='name',
            field=models.CharField(blank=True, db_comment='氏名', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='name_katakana',
            field=models.CharField(blank=True, db_comment='カタカナ氏名', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(blank=True, db_comment='注文作成日', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.IntegerField(blank=True, db_comment='支払金額: =総金額＋配送料-クーポン', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, db_comment='支払い番号:paypay\u3000支払い番号', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(db_comment='注文ステータス:"01作成済み"、"02支払い待ち"、"03支払い済み"、"04発送済み"、"05完了"、"06キャンセル"'),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_comment='更新日時'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='item_id',
            field=models.CharField(db_comment='注文アイテムID', max_length=50, primary_key=True, serialize=False),
        ),
    ]
