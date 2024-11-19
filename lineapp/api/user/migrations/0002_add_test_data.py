# api/user/migrations/0002_add_test_data.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL([
            # 插入用户数据
            """
            INSERT INTO users (
                id, line_user_id, mail, user_name, role, deleted_flag, 
                token_usage, birthday, gender, phone_number, created_at, updated_at
            ) VALUES
            ('USER001', 'LINE001', 'taro@example.com', 'Taro Yamada', 1, FALSE, 
             50, '1990-01-01', 'm', '090-1234-5678', NOW(), NOW()),
            ('USER002', 'LINE002', 'hanako@example.com', 'Hanako Suzuki', 1, FALSE, 
             30, '1995-02-02', 'f', '080-2345-6789', NOW(), NOW()),
            ('01JCQFAYQW3W54S7P3PPM4M7DG', 'LINE003', 'test@example.com', 'Test User', 1, FALSE,
             0, '1990-01-01', 'm', '080-9876-5432', NOW(), NOW())
            """,
            
            # 插入地址数据
            """
            INSERT INTO user_addresses (
                address_id, user_id, last_name, first_name, last_name_katakana, 
                first_name_katakana, phone_number, prefecture_address, city_address, 
                district_address, detail_address, postal_code, is_default, 
                created_at, updated_at, updated_by, created_by, deleted_flag
            ) VALUES 
            ('ADDR001', 'USER001', '山田', '太郎', 'ヤマダ', 'タロウ', 
             '090-1234-5678', '東京都', '新宿区', '西新宿', '1-1-1', 
             '123-4567', TRUE, NOW(), NOW(), 'USER001', 'USER001', FALSE),
             
            ('ADDR002', 'USER002', '鈴木', '花子', 'スズキ', 'ハナコ', 
             '080-2345-6789', '大阪府', '北区', '梅田', '1-2-3', 
             '234-5678', FALSE, NOW(), NOW(), 'USER002', 'USER002', FALSE),
             
            ('01JCZB48SD2SR5V55METQP05N9', '01JCQFAYQW3W54S7P3PPM4M7DG', '山田123', '太郎456', 'ヤマダ', 
             'タロ', '080-9876-5432', '东京都', '中京区', '二条通河原町', '西入る', 
             '600-8001', FALSE, '2024-11-18 18:54:42.596', '2024-11-18 18:54:42.596', 
             '01JCQFAYQW3W54S7P3PPM4M7DG', '01JCQFAYQW3W54S7P3PPM4M7DG', FALSE),
             
            ('01JCZB4HVXPFFS22HB1ES448AG', '01JCQFAYQW3W54S7P3PPM4M7DG', '山田', '太郎', 'ヤマダ', 
             'タロ', '080-9876-5432', '东京都', '中京区', '二条通河原町', '西入る', 
             '600-8001', TRUE, '2024-11-18 18:54:52.028', '2024-11-18 18:54:52.028',
             '01JCQFAYQW3W54S7P3PPM4M7DG', '01JCQFAYQW3W54S7P3PPM4M7DG', FALSE)
            """
        ],
        reverse_sql=[
            "DELETE FROM user_addresses",
            "DELETE FROM users"
        ])
    ]