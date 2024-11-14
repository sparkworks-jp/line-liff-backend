# api/line_auth.py
from functools import wraps
import jwt
import requests
import logging
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class LineAuthentication:
    """LINE認証ツール"""

    def get_line_keys(self):
        """LINE公開鍵を取得"""
        logger.info("1. LINE公開鍵の取得を開始")
        try:
            response = requests.get(
                'https://api.line.me/oauth2/v2.1/keys',
                timeout=10
            )
            logger.info(f"2. LINE APIレスポンス: status={response.status_code}")
            logger.debug(f"2-1. レスポンス本文: {response.text}")
            
            if response.status_code != 200:
                logger.error(f"3. LINE公開鍵の取得失敗: {response.status_code}")
                raise Exception('LINE公開鍵の取得に失敗しました')
                
            keys = response.json()['keys']
            logger.info(f"3. 公開鍵取得成功: {len(keys)}個の鍵を取得")
            return keys
            
        except Exception as e:
            logger.error(f"X. 公開鍵取得エラー: {str(e)}", exc_info=True)
            raise

    def verify_id_token(self, id_token):
        """LINE IDトークンを検証"""
        try:
            logger.info("4. トークン検証開始")
            # トークンの先頭部分のみログ出力（セキュリティのため）
            logger.info(f"4-1. 検証するトークン: {id_token[:20]}...")
            
            # トークンヘッダーからkidとアルゴリズムを取得
            header = jwt.get_unverified_header(id_token)
            kid = header.get('kid')
            alg = header.get('alg', 'RS256')
            logger.info(f"5. トークンヘッダー情報: kid={kid}, alg={alg}")

            # 公開鍵を取得
            keys = self.get_line_keys()
            key = next((k for k in keys if k['kid'] == kid), None)
            if not key:
                logger.error(f"6. 対応する公開鍵が見つかりません。kid={kid}")
                raise jwt.InvalidTokenError('対応する公開鍵が見つかりません')
            logger.info("6. 対応する公開鍵を発見")

            # トークンを検証
            jwk_algorithm = jwt.algorithms.ECAlgorithm if alg == 'ES256' else jwt.algorithms.RSAAlgorithm
            logger.info(f"7. トークン検証開始: アルゴリズム={alg}")
            
            decoded = jwt.decode(
                id_token,
                jwk_algorithm.from_jwk(key),
                algorithms=[alg],
                audience=settings.LINE_LIFF_ID,
                issuer='https://access.line.me'
            )
            
            logger.info("8. トークン検証成功")
            logger.debug(f"8-1. デコード結果: {decoded}")
            return decoded

        except jwt.ExpiredSignatureError as e:
            logger.error("X. トークン期限切れ", exc_info=True)
            raise Exception('トークンの有効期限が切れています')
        except jwt.InvalidTokenError as e:
            logger.error(f"X. 無効なトークン: {str(e)}", exc_info=True)
            raise Exception(f'無効なトークンです: {str(e)}')
        except Exception as e:
            logger.error(f"X. 検証エラー: {str(e)}", exc_info=True)
            raise Exception(f'トークン検証エラー: {str(e)}')


class LineAuthMiddleware(MiddlewareMixin):
    """LINE認証ミドルウェア"""

    def process_request(self, request):
        """リクエストの認証処理"""
        logger.info(f"===== 認証処理開始 =====")
        logger.info(f"リクエストパス: {request.path}")
        logger.debug(f"リクエストヘッダー: {dict(request.headers)}")

        # 認証除外パス
        EXEMPT_PATHS = ['/admin/', '/api/webhook/', '/api/public/', '/static/']
        if any(request.path.startswith(path) for path in EXEMPT_PATHS):
            logger.info(f"認証除外パス: {request.path}")
            return None

        # Authorizationヘッダーの検証
        auth_header = request.headers.get('Authorization', '')
        logger.info(f"Authorizationヘッダー: {auth_header[:30]}...")

        if not auth_header.startswith('Bearer '):
            logger.error("認証ヘッダーが不正です")
            return JsonResponse({'error': '認証が必要です'}, status=401)

        try:
            # トークンを検証してユーザー情報を取得
            token = auth_header.split(' ')[1]
            auth = LineAuthentication()
            user_info = auth.verify_id_token(token)
            
            # ユーザー情報をrequestに追加
            request.line_user = user_info
            request.line_user_id = user_info.get('sub')
            logger.info(f"認証成功: user_id={request.line_user_id}")
            
        except Exception as e:
            logger.error(f"認証失敗: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=401)
        
        logger.info("===== 認証処理完了 =====")


def line_auth_required(view_func):
    """LINE認証必須デコレーター"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        logger.info(f"デコレーターチェック: {view_func.__name__}")
        
        if not hasattr(request, 'line_user'):
            logger.error(f"認証必要: {view_func.__name__}")
            return JsonResponse({'error': 'LINE認証が必要です'}, status=401)
            
        logger.info(f"認証OK: {view_func.__name__}")
        return view_func(request, *args, **kwargs)
    return wrapper