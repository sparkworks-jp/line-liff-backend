# Generated by Django 4.2.5 on 2024-12-04 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_rename_id_user_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='line_user_id',
            field=models.CharField(db_comment='lineユーザー番号', default='Uf1e196438ad2e407c977f1ede4a39580', max_length=256, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='mail',
            field=models.CharField(blank=True, db_comment='メールアドレス', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, db_comment='電話番号', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.IntegerField(db_comment='ロール:0:user, 1:admin'),
        ),
    ]
