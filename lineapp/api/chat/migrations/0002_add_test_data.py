
# api/chat/migrations/0002_add_test_data.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL([
            """
            INSERT INTO chat_histories (
                chat_id, questions, answers, token_utilization, thread_id,
                created_by, updated_by, deleted_flag, updated_at, created_at
            ) VALUES
            ('CHAT001', 'What is the order status?', 'Your order has been shipped.',
             50, 'THREAD001', 'user001', 'user001', FALSE, NOW(), NOW()),
            ('CHAT002', 'Where is my tracking number?', 'Your tracking number is TRK98765432.',
             40, 'THREAD002', 'user002', 'user002', FALSE, NOW(), NOW())
            """
        ],
        reverse_sql=[
            "DELETE FROM chat_histories"
        ])
    ]