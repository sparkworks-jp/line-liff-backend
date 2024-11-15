from functools import wraps
import jwt
import requests
import logging
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime

logger = logging.getLogger(__name__)

class LineAuthentication:
    """LINE認証ツール"""

    def get_line_keys(self):
        """LINE公開鍵を取得"""
        logger.info("1. LINE公開鍵の取得を開始")
        try:
            response = requests.get(
                'https://api.line.me/oauth2/v2.1/certs',
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
            logger.info("=== トークン検証開始 ===")
            logger.info(f"設定されているLIFF ID: {settings.LINE_LIFF_ID}")
            
            # 解码 token 查看实际的 audience（无需验证签名）
            try:
                unverified_payload = jwt.decode(id_token, options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False
                })
                logger.info(f"トークンの中身: {unverified_payload}")
                logger.info(f"トークンのaudience: {unverified_payload.get('aud')}")

                # LINE LIFF SDK 的行为 - 它在生成 token 时可能只使用了 channel ID 作为 audience。
                token_aud = unverified_payload.get('aud')
                setting_channel_id = settings.LINE_LIFF_ID.split('-')[0] 
                if token_aud != setting_channel_id:
                    logger.error(f"Channel ID不一致: token={token_aud}, setting={setting_channel_id}")
                    raise jwt.InvalidTokenError(
                        f"Channel ID不一致: トークン={token_aud}, 設定={setting_channel_id}"
                    )
            except Exception as e:
                logger.error(f"トークン解析エラー: {str(e)}")
                raise

            # 获取 token 头部信息
            header = jwt.get_unverified_header(id_token)
            kid = header.get('kid')
            alg = header.get('alg', 'RS256')
            logger.info(f"トークンヘッダー情報: kid={kid}, alg={alg}")
            
            if not kid:
                raise jwt.InvalidTokenError('トークンヘッダーにkidがありません')
                
            # 获取公钥
            keys = self.get_line_keys()
            key = next((k for k in keys if k['kid'] == kid), None)
            
            if not key:
                raise jwt.InvalidTokenError('対応する公開鍵が見つかりません')
                
            # 验证签名并解码
            jwk_algorithm = jwt.algorithms.ECAlgorithm if alg == 'ES256' else jwt.algorithms.RSAAlgorithm
            public_key = jwk_algorithm.from_jwk(key)
            
            decoded = jwt.decode(
                id_token,
                public_key,
                algorithms=[alg],
                audience=setting_channel_id,
                issuer='https://access.line.me'
            )
            
            logger.info("トークン検証成功")
            logger.debug(f"検証結果: {decoded}")
            return decoded
                
        except jwt.ExpiredSignatureError:
            logger.error("トークン期限切れ")
            raise Exception('トークンの有効期限が切れています')
            
        except jwt.InvalidTokenError as e:
            logger.error(f"無効なトークン: {str(e)}")
            raise Exception(f'無効なトークンです: {str(e)}')
            
        except Exception as e:
            logger.error(f"検証エラー: {str(e)}")
            raise Exception(f'トークン検証エラー: {str(e)}')


class LineAuthMiddleware(MiddlewareMixin):
    """LINE認証ミドルウェア"""

    def process_request(self, request):
        """リクエストの認証処理"""
        logger.info(f"===== 認証処理開始 =====")
        logger.info(f"リクエストパス: {request.path}")
        logger.debug(f"リクエストヘッダー: {dict(request.headers)}")

        # 认证豁免路径检查
        EXEMPT_PATHS = ['/admin/', '/api/webhook/', '/api/public/', '/static/']
        if any(request.path.startswith(path) for path in EXEMPT_PATHS):
            logger.info(f"認証除外パス: {request.path}")
            return None

        # 验证 Authorization 头
        auth_header = request.headers.get('Authorization', '')
        logger.info(f"Authorizationヘッダー: {auth_header[:30]}...")

        if not auth_header.startswith('Bearer '):
            logger.error("認証ヘッダーが不正です")
            return JsonResponse({'error': '認証が必要です'}, status=401)

        try:
            # 验证 token 并获取用户信息
            token = auth_header.split(' ')[1]
            auth = LineAuthentication()
            user_info = auth.verify_id_token(token)
            logger.debug(f"verify_id_token 返回值: {user_info}")

            # 添加额外的验证确保 user_info 不为 None
            if user_info is None:
                logger.error("トークン検証でユーザー情報が取得できませんでした")
                return JsonResponse({'error': 'トークン検証に失敗しました'}, status=401)
            
            # 确保必要的字段存在
            if 'sub' not in user_info:
                logger.error("ユーザーIDが見つかりません")
                return JsonResponse({'error': 'ユーザー情報が不完全です'}, status=401)
            
            # 设置用户信息
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