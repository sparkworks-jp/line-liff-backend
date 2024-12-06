import os
import logging
import asyncio
from datetime import datetime
import ulid
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from openai import AsyncOpenAI
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from .models import ChatHistory,Thread

logger = logging.getLogger("django")

# Line Bot配置
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

api_key = os.getenv('OPEN_AI_API_KEY')
assistant_id = os.getenv('OPENAI_ASSISTANT_ID')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(CHANNEL_SECRET)

@webhook_handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """受信したテキストメッセージを処理する"""
    logger.info(f"メッセージを受信しました。User ID: {event.source.user_id}")
    try:        
        # 待機メッセージを送信
        logger.info(f"待機メッセージを送信します。Reply Token: {event.reply_token}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="検索中です。しばらくお待ちください...")
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # 获取AI响应
            response = loop.run_until_complete(chat_by_line(event.message.text))
            logger.info("メッセージ処理が完了しました")     
            if response.get('history_data'):
                save_task = loop.create_task(save_history_async(response['history_data']))
                logger.info("履歴の保存が完了しました")
            flex_message = {
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": response.get('content', 'コンテンツが見つかりません'),
                                    "wrap": True,
                                    "size": "md",
                                    "maxLines": 0
                                }
                            ]
                        }
                    }
                ]
            }

            logger.info("Flexメッセージを送信します")
            line_bot_api.push_message(
                event.source.user_id,
                FlexSendMessage(alt_text='Flexメッセージ', contents=flex_message)
            )
            logger.info("メッセージ送信が完了しました")

        finally:
            loop.run_forever()
            loop.call_soon_threadsafe(loop.stop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    except Exception as e:
        logger.error(f"メッセージ処理中にエラーが発生しました: {str(e)}")
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text="メッセージの処理中にエラーが発生しました。")
        )

@csrf_exempt
@require_POST
@api_view(['POST'])
def line_webhook(request):
    """Line Webhookのリクエスト処理"""
    logger.info("LINE Webhookリクエストを受信しました")
    try:
        signature = request.headers['X-Line-Signature']
        logger.info(f"署名を検証します: {signature}")
        body = request.body.decode()
        
        webhook_handler.handle(body, signature)
        logger.info("Webhookの処理が正常に完了しました")
        return Response('OK')
        
    except InvalidSignatureError:
        logger.error("無効な署名です")
        return Response('Invalid signature')
    except Exception as e:
        logger.error(f"Webhook ERROR: {str(e)}")
        return Response(status=500)

async def poll_run_status(client, thread_id, run_id, max_attempts=100, delay=0.5):
    """Poll OpenAI run status until completion or timeout"""
    logger.info(f"ステータス確認開始 - Thread ID: {thread_id}, Run ID: {run_id}")
    for attempt in range(max_attempts):
        logger.info(f"ステータス確認試行 {attempt + 1}/{max_attempts}")
        run = await client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run.status not in ['queued', 'in_progress']:
            logger.info(f"ステータス確認完了: {run.status}")
            return run
        await asyncio.sleep(delay)
    logger.error("ステータス確認がタイムアウトしました")
    raise TimeoutError("Run status polling timed out")

async def save_history(history_data, max_retries=3):
    """Save chat ChatHistory with retry mechanism"""
    for attempt in range(max_retries):
        try:
            await sync_to_async(ChatHistory.objects.create)(**history_data)
            logger.info(f"ChatHistory saved successfully for thread {history_data['thread_id']}")
            return
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: Error saving ChatHistory: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0)
            else:
                logger.error(f"Failed to save ChatHistory after {max_retries} attempts")
                raise

async def save_history_async(history_data):
    try:
        logger.info(f"開始履歴保存 - Thread ID: {history_data.get('thread_id')}")
        await save_history(history_data)
        logger.info(f"履歴保存成功 - Thread ID: {history_data.get('thread_id')}")
    except Exception as e:
        error_message = f"""
                        データベース保存エラー
                        Time: {datetime.now()}
                        Error: {str(e)}
                        Thread ID: {history_data.get('thread_id')}
                        Questions: {history_data.get('questions')}
                        """
        logger.error(error_message)
        
        try:
            error_history = {
                'chat_id': str(ulid.new()),
                'questions': history_data.get('questions'),
                'answers': error_message,
                'token_utilization': 0,
                'thread_id': history_data.get('thread_id'),
                'created_by': history_data.get('created_by', 'system'),
                'updated_by': history_data.get('updated_by', 'system')
            }
            await save_history(error_history)
            logger.info("エラー履歴を保存しました")
        except Exception as save_error:
            logger.error(f"エラー履歴の保存にも失敗しました: {str(save_error)}")


async def get_thread(user_id):
    logger.info(f"スレッド取得開始 - User ID: {user_id}")
    try:
        thread = await sync_to_async(Thread.objects.get)(
            user_id=user_id,
            deleted_flag=False
        )
        logger.info(f"スレッド取得成功 - Thread ID: {thread.id}")
        return {
            'thread_id': thread.id,
            'openai_thread_id': thread.openai_thread_id
        }
    except Thread.DoesNotExist:
        logger.info(f"スレッドが存在しません - User ID: {user_id}")
        return None


async def create_thread(user_id, api_key):
    logger.info(f"新規スレッド作成開始 - User ID: {user_id}")
    client = AsyncOpenAI(api_key=api_key)
    openai_thread = await client.beta.threads.create()
    logger.info(f"OpenAIスレッド作成完了 - Thread ID: {openai_thread.id}")

    thread = await sync_to_async(Thread.objects.create)(
        user_id=user_id,
        openai_thread_id=openai_thread.id,
        created_by=user_id,
        updated_by=user_id
    )
    logger.info(f"データベースにスレッドを保存しました - Thread ID: {thread.id}")

    return {
        'thread_id': thread.id,
        'openai_thread_id': thread.openai_thread_id
    }


async def chat_by_line(message_text):
    """Line メッセージ処理ロジック"""
    try:
        user_id = "Uf1e196438ad2e407c977f1ede4a39580" 
        api_key = os.getenv('OPEN_AI_API_KEY')
        assistant_id = os.getenv('OPENAI_ASSISTANT_ID')

        logger.info(f"リクエスト受信 - User ID: {user_id}")

        if not api_key:
            logger.error("API keyが設定されていません")
            return Response(
                {"error": "API key not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if not message_text :
            logger.error("無効なリクエストデータです")
            return Response(
                {"error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )

        thread_data = await get_thread(user_id)
        if not thread_data:
            logger.info("新規スレッドを作成します")
            thread_data = await create_thread(user_id, api_key)

        thread_id = thread_data['openai_thread_id']
        logger.info(f"処理対象スレッド - Thread ID: {thread_id}")

        client = AsyncOpenAI(api_key=api_key)
        logger.info("メッセージを作成します")
        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_text
        )

        logger.info("Assistantの実行を開始します")
        run = await client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        run = await poll_run_status(client, thread_id, run.id)


        if run.status == 'completed':
            logger.info("Assistant処理が完了しました")
            message_list = await client.beta.threads.messages.list(
                thread_id=thread_id
            )
            assistant_reply = message_list.data[0].content[0].text.value
            token_usage = run.usage.total_tokens if run.usage else 0
           
            logger.info(f"assistant_reply: {assistant_reply}")
            logger.info(f"トークン使用量: {token_usage}")


            logger.info("履歴を保存します")
            history_data = {
                'chat_id': str(ulid.new()),
                'questions': message_text,
                'answers': assistant_reply,
                'token_utilization': token_usage,
                'thread_id': thread_id,
                'created_by': user_id,
                'updated_by': user_id
            }            

            return {
                'content': assistant_reply,
                'status': 'completed',
                'history_data': history_data 
            }

        logger.info(f"実行ステータス: {run.status}")
        return {
            'content': '処理が完了していません',
            'status': run.status
        }
    except Exception as e:
        logger.error(f"メッセージ処理中にエラーが発生しました: {str(e)}")
        return {
            'content': 'エラーが発生しました',
            'status': 'error'
        }
    

