from django.db import models

class OrderItem(models.Model):
    item_id = models.CharField(max_length=50, primary_key=True, db_comment='注文アイテムID')
    order_id = models.CharField(max_length=50, db_comment='注文番号')
    product_id = models.CharField(max_length=50, db_comment='商品番号')
    product_name = models.CharField(max_length=255, db_comment='商品名')
    product_price = models.IntegerField(db_comment='商品価格')
    product_size_information = models.TextField(null=True, blank=True, db_comment='商品サイズ情報:（json数组-重量，体积，规格等）_具体待定')
    product_store_barcode = models.CharField(max_length=100, null=True, blank=True, db_comment='倉庫バーコード')
    account = models.IntegerField(db_comment='購入数量')
    subtotal = models.IntegerField(db_comment='小計金額')
    remark = models.TextField(null=True, blank=True, db_comment='顧客の商品の備考')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')
    updated_by = models.CharField(max_length=256, null=True, blank=True, db_comment='更新者')
    created_by = models.CharField(max_length=256, null=True, blank=True, db_comment='登録者')
    deleted_flag = models.BooleanField(null=True, blank=True, db_comment='削除フラグ')

    class Meta:
        db_table = 'order_items'
        db_table_comment = '注文アイテム'


class Coupon(models.Model):
    coupon_id = models.CharField(primary_key=True, max_length=256)
    coupon_code = models.CharField(unique=True, max_length=20)
    coupon_name = models.CharField(max_length=256)
    discount_type = models.SmallIntegerField(
        choices=[
            (1, '定額割引'),
            (2, 'パーセント割引')
        ]
    )
    discount_value = models.DecimalField(max_digits=10,decimal_places=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    min_order_amount = models.DecimalField(
        max_digits=10, 
        null=True, 
        blank=True,decimal_places=0
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        null=True, 
        blank=True,decimal_places=0
    )
    usage_count = models.IntegerField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.CharField(max_length=256, null=True, blank=True)
    deleted_flag = models.BooleanField(default=False, null=True)
    product_id = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        db_table = 'coupons'
        db_table_comment = 'クーポン管理テーブル'

    def __str__(self):
        return f"{self.coupon_code} - {self.coupon_name}"


class Order(models.Model):
    order_id = models.CharField(max_length=50, primary_key=True, db_comment='注文番号')
    user_id = models.CharField(max_length=50, db_comment='ユーザーID')
    coupon_id = models.CharField(null=True,blank=True,max_length=50, db_comment='クーポンID')
    discount_amount = models.DecimalField(null=True,blank=True,max_digits=10, db_comment='割引額',decimal_places=0)
    order_date = models.DateTimeField(null=True,blank=True,db_comment='注文作成日')
    carriage = models.IntegerField(null=True, blank=True, db_comment='配送料')
    total_price = models.IntegerField(null=True, blank=True, db_comment='総金額')
    coupon_count = models.IntegerField(null=True, blank=True, db_comment='クーポン金額:=総商品のprice')
    payment = models.IntegerField(null=True, blank=True, db_comment='支払金額: =総金額＋配送料-クーポン')
    status = models.IntegerField(db_comment='注文ステータス:"01作成済み"、"02支払い待ち"、"03支払い済み"、"04発送済み"、"05完了"、"06キャンセル"')
    tracking_number = models.CharField(max_length=50, db_comment='追跡番号')
    shipment_date = models.DateTimeField(null=True, blank=True, db_comment='発送日')
    payment_date = models.DateTimeField(null=True, blank=True, db_comment='支払日')
    payment_qr_code_id= models.CharField(db_comment='支払い検証クラスID', max_length=50)
    payment_id = models.CharField(max_length=10, null=True, blank=True, db_comment='支払い番号:paypay　支払い番号')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')
    updated_by = models.CharField(max_length=256, null=True, blank=True, db_comment='更新者')
    created_by = models.CharField(max_length=256, null=True, blank=True, db_comment='登録者')
    deleted_flag = models.BooleanField(null=True, blank=True, db_comment='削除フラグ')
    address = models.TextField(null=True, blank=True, db_comment='配送先住所')
    name_katakana = models.CharField(max_length=256, null=True, blank=True, db_comment='カタカナ氏名')
    name = models.CharField(max_length=256, null=True, blank=True, db_comment='氏名')
    phone_number = models.CharField(max_length=50, null=True, blank=True, db_comment='電話番号')
    postal_code = models.CharField(max_length=50, null=True, blank=True, db_comment='郵便番号')


    class Meta:
        db_table = 'orders'
        db_table_comment = '注文'