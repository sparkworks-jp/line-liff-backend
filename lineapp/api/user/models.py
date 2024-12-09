

from django.db import models
class UserAddress(models.Model):
    address_id = models.CharField(max_length=50, primary_key=True, db_comment='住所ID')
    user_id = models.CharField(max_length=50, db_comment='ユーザーID')
    last_name = models.CharField(max_length=50, db_comment='姓')
    first_name = models.CharField(max_length=50, db_comment='名')
    last_name_katakana = models.CharField(max_length=50, db_comment='カタカナ_姓')
    first_name_katakana = models.CharField(max_length=50, db_comment='カタカナ_名')
    phone_number = models.CharField(max_length=50, db_comment='電話番号')
    prefecture_address = models.CharField(max_length=255, db_comment='都道府県:都道府県-东京都/大阪府/奈良県')
    city_address = models.CharField(max_length=255, db_comment='市区町村:市区町村-中野区/台东区')
    district_address = models.CharField(max_length=255, null=True, blank=True, db_comment='地区:地区-道玄坂(东京都渋谷区道玄坂)')
    detail_address = models.CharField(max_length=255, db_comment='具体アドレス:具体地址----街道-建筑物-门牌号')
    postal_code = models.CharField(max_length=50, db_comment='郵便番号')
    is_default = models.BooleanField(default=False, db_comment='デフォルトの住所')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')
    updated_by = models.CharField(max_length=256, null=True, blank=True, db_comment='更新者')
    created_by = models.CharField(max_length=256, null=True, blank=True, db_comment='登録者')
    deleted_flag = models.BooleanField(null=True, blank=True, db_comment='削除フラグ')

    class Meta:
        db_table = 'user_addresses'
        db_table_comment = '住所'

class User(models.Model):
    user_id = models.CharField(max_length=256, primary_key=True, db_comment='ユーザーID')
    line_user_id = models.CharField(max_length=256, unique=True,  db_comment='lineユーザー番号')
    mail = models.CharField(null=True, blank=True,max_length=256, db_comment='メールアドレス')
    user_name = models.CharField(null=True,blank=True,max_length=256, db_comment='ユーザー名')
    role = models.IntegerField(db_comment='ロール:user:0, admin:1')
    deleted_flag = models.BooleanField(default=False, db_comment='削除フラグ')
    token_usage = models.IntegerField(default=0, db_comment='トークン使用量')
    birthday = models.DateField(null=True, blank=True, db_comment='生年月日')
    gender = models.CharField(max_length=1, null=True, blank=True, db_comment='性別:m:man f:female')
    phone_number = models.CharField(null=True, blank=True,max_length=20, db_comment='電話番号')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')
    updated_by = models.CharField(max_length=256, null=True, blank=True, db_comment='更新者')
    created_by = models.CharField(max_length=256, null=True, blank=True, db_comment='登録者')


    class Meta:
        db_table = 'users'
        db_table_comment = 'ユーザー'