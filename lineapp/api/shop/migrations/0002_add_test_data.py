from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL([
            """
            INSERT INTO products (
                product_id, product_name, image, description, allergens,
                product_price, product_marque, product_store_barcode,
                product_size_information, sale_status, created_at, updated_at,
                updated_by, created_by, deleted_flag, webpageUrl
            ) VALUES
            ('PROD001', 'らせん酥（螺旋酥）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/rasensu.jpg',
             'A tasty spiral pastry', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK001', 'BAR123456', 'Weight: 100g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/index.html'),
            
            ('PROD003', 'たんこう酥（蛋黄酥）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/tankōsu.png',
             'Egg yolk pastry', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK002', 'BAR654321', 'Weight: 120g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/index.html'),
            
            ('PROD002', '緑豆ケーキ(绿豆糕)', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/midorikeiki.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK003', 'BAR789012', 'Weight: 110g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://www.rakuten.ne.jp/gold/kasyou-morin/'),
            
            ('PROD004', 'アーモンドパイ(杏仁酥)', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/aamonndopai.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK004', 'BAR345678', 'Weight: 115g', 1, NOW(), NOW(), NULL, NULL, false,
             'http://localhost:9000/shop/4'),
            
            ('PROD005', '揚げひねりパン（麻花）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/agehineripann.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK005', 'BAR901234', 'Weight: 105g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD006', '月餅', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/geppei.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK006', 'BAR567890', 'Weight: 125g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD007', '大福（だいふく）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/daifuku.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK007', 'BAR123789', 'Weight: 95g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD008', '羊羹（ようかん）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/cappuccino.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             340, 'SNACK008', 'BAR456123', 'Weight: 100g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD009', 'にくまつケーキ（肉松蛋糕）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/nikumatsu.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK009', 'BAR789456', 'Weight: 130g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD010', 'エッグタルト（蛋挞）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/eggutarto.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK010', 'BAR234567', 'Weight: 90g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD011', 'ほうり酥（凤梨酥）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/hōrisu.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK011', 'BAR345678', 'Weight: 110g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD012', 'りょくとう餅（绿豆饼）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/ryokutō.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK012', 'BAR456789', 'Weight: 115g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD013', 'なつめに酥（枣泥酥）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/natsumenisu.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK013', 'BAR567890', 'Weight: 105g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD014', 'ゆうご（油果）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/yūgo.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK014', 'BAR678901', 'Weight: 95g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD015', 'ブラウニー（布朗尼）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/buraunī.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK015', 'BAR789012', 'Weight: 120g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/'),
            
            ('PROD016', 'マカロン（马卡龙）', 'https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/makaron.jpg',
             '蛋黄酥は台湾の月餅から派生した伝統菓子で...', '卵や乳製品などのアレのアレルゲン物質を使わないでつくった、食物アレルギーを持った方でも安心して食べられるケーキです',
             500, 'SNACK015', 'BAR789012', 'Weight: 120g', 1, NOW(), NOW(), NULL, NULL, false,
             'https://sparkworks.co.jp/')
            """
        ],
        reverse_sql=[
            "DELETE FROM products"
        ])
    ]