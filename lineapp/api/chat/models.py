from django.db import models
class ChatHistory(models.Model):
    chat_id = models.CharField(max_length=50, primary_key=True, db_comment='チャットID')
    questions = models.TextField(null=True, blank=True, db_comment='問題')
    answers = models.TextField(null=True, blank=True, db_comment='答え')
    token_utilization = models.IntegerField(db_comment='token消費量')
    thread_id = models.CharField(max_length=256, null=True, blank=True, db_comment='スレッドID')
    created_by = models.CharField(max_length=256, null=True, blank=True, db_comment='作成者')
    updated_by = models.CharField(max_length=256, null=True, blank=True, db_comment='更新者')
    deleted_flag = models.BooleanField(null=True, blank=True, db_comment='削除フラグ')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新日時')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='作成日時')

    class Meta:
        db_table = 'chat_histories'
        db_table_comment = 'チャット歴史'

class Thread(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=256
    )
    openai_thread_id = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )
    user_id = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True
    )
    updated_by = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )
    created_by = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )
    deleted_flag = models.BooleanField(
        null=True,
        default=False
    )

    class Meta:
        db_table = 'threads'
