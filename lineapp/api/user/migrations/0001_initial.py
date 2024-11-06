# Generated by Django 4.2.5 on 2024-11-06 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(db_comment='ユーザーID', max_length=256, primary_key=True, serialize=False)),
                ('line_user_id', models.CharField(blank=True, db_comment='lineユーザー番号', max_length=256, null=True)),
                ('mail', models.CharField(db_comment='メールアドレス', max_length=256)),
                ('user_name', models.CharField(db_comment='ユーザー名', max_length=256)),
                ('role', models.IntegerField(db_comment='ロール:0:admin, 1:user')),
                ('deleted_flag', models.BooleanField(db_comment='削除フラグ', default=False)),
                ('token_usage', models.IntegerField(db_comment='トークン使用量', default=0)),
                ('birthday', models.DateField(blank=True, db_comment='生年月日', null=True)),
                ('gender', models.CharField(blank=True, db_comment='性別:m:man f:female', max_length=1, null=True)),
                ('phone_number', models.CharField(db_comment='電話番号', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_comment='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, db_comment='更新日時')),
                ('updated_by', models.CharField(blank=True, db_comment='更新者', max_length=256, null=True)),
                ('created_by', models.CharField(blank=True, db_comment='登録者', max_length=256, null=True)),
            ],
            options={
                'db_table': 'line.users',
                'db_table_comment': 'ユーザー',
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('address_id', models.CharField(db_comment='住所ID', max_length=50, primary_key=True, serialize=False)),
                ('user_id', models.CharField(db_comment='ユーザーID', max_length=50)),
                ('last_name', models.CharField(db_comment='姓', max_length=50)),
                ('first_name', models.CharField(db_comment='名', max_length=50)),
                ('last_name_katakana', models.CharField(db_comment='カタカナ_姓', max_length=50)),
                ('first_name_katakana', models.CharField(db_comment='カタカナ_名', max_length=50)),
                ('phone_number', models.CharField(db_comment='電話番号', max_length=50)),
                ('prefecture_address', models.CharField(db_comment='都道府県:都道府県-东京都/大阪府/奈良県', max_length=255)),
                ('city_address', models.CharField(db_comment='市区町村:市区町村-中野区/台东区', max_length=255)),
                ('district_address', models.CharField(blank=True, db_comment='地区:地区-道玄坂(东京都渋谷区道玄坂)', max_length=255, null=True)),
                ('detail_address', models.CharField(db_comment='具体アドレス:具体地址----街道-建筑物-门牌号', max_length=255)),
                ('postal_code', models.CharField(db_comment='郵便番号', max_length=50)),
                ('is_default', models.BooleanField(db_comment='デフォルトの住所', default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_comment='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, db_comment='更新日時')),
                ('updated_by', models.CharField(blank=True, db_comment='更新者', max_length=256, null=True)),
                ('created_by', models.CharField(blank=True, db_comment='登録者', max_length=256, null=True)),
                ('deleted_flag', models.BooleanField(blank=True, db_comment='削除フラグ', null=True)),
            ],
            options={
                'db_table': 'line.user_addresses',
                'db_table_comment': '住所',
            },
        ),
    ]
