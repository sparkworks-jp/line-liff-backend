from django.db import models
class Product(models.Model):
    product_id = models.CharField(max_length=50, primary_key=True, db_comment='商品番号')
    product_name = models.CharField(max_length=255, db_comment='商品名')
    image = models.URLField(null=True, blank=True, db_comment='商品画像URL')     
    description = models.TextField(null=True, blank=True, db_comment='商品説明')
    webpageUrl = models.URLField( max_length=2083,null=True,blank=True,db_comment='サイトURL')
    allergens = models.CharField(max_length=255, null=True, blank=True, db_comment='アレルゲン')  
    product_price = models.IntegerField(db_comment='商品価格')
    product_marque = models.CharField(max_length=100, null=True, blank=True, db_comment='商品型番:商品型号，待定')
    product_store_barcode = models.CharField(max_length=100, null=True, blank=True, db_comment='商品の倉庫バーコード')
    product_size_information = models.CharField(max_length=255, null=True, blank=True, db_comment='商品サイズ情報:（json数组-重量，体积，规格等）')
    sale_status = models.IntegerField(null=True, blank=True, db_comment='販売状況:"01販売中，02販売停止"')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')
    updated_by = models.CharField(max_length=256, null=True, blank=True, db_comment='更新者')
    created_by = models.CharField(max_length=256, null=True, blank=True, db_comment='登録者')
    deleted_flag = models.BooleanField(null=True, blank=True, db_comment='削除フラグ')


    class Meta:
        db_table = 'products'
        db_table_comment = '商品'