# Generated by Django 4.2.5 on 2024-11-12 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, db_comment='商品画像URL', null=True, upload_to='products/'),
        ),
    ]
