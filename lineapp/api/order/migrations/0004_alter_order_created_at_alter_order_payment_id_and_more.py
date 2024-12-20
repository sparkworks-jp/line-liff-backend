# Generated by Django 4.2.5 on 2024-11-25 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_coupon_coupon_id_alter_coupon_discount_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_comment='作成日時', null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, db_comment='支払い番号:paypay\u3000支払い番号', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_qr_code_id',
            field=models.CharField(blank=True, db_comment='支払い検証クラスID', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, db_comment='追跡番号', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_comment='更新日時', null=True),
        ),
    ]
