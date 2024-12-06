from functools import wraps
import os
import jwt
import requests
import logging
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime
from django.db import transaction
import ulid

from core.utils.LineKeyManager import LineKeyManager

logger = logging.getLogger(__name__)

class LineAuthentication:
    """LINE認証ツール"""

    def verify_id_token(self, id_token):
        """LINE IDトークンを検証"""
        try:
            logger.info("=== トークン検証開始 ===")
            logger.info(f"設定されているLIFF ID: {settings.LINE_LIFF_ID}")
            
            try:
                unverified_payload = jwt.decode(id_token, options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False
                })
                # todo 事前チェック 実際にはaudience検証のみを行う
                # 主に不要なネットワークリクエストを減らすため、公開鍵の取得なしで明らかなエラーを検出できる
                # これは事前チェックステップで、トークンの構造が正しいか、特にaudience値を確認することが目的
                # この時点では完全な検証は行わない理由：
                # まだ公開鍵を取得していないため、署名を検証できない
                # トークンの基本構造とコンテンツが正しいかを先に確認する必要がある
                # トークンからkid（鍵ID）を取得して、適切な公開鍵を選択する必要がある

                logger.info(f"トークンの中身: {unverified_payload}")
                logger.info(f"トークンのaudience: {unverified_payload.get('aud')}")
                # LINE LIFF SDKの動作 - トークン生成時にchannel IDのみをaudienceとして使用する
                token_aud = unverified_payload.get('aud')
                setting_channel_id = os.getenv('CHANNEL_ID')
                if token_aud != setting_channel_id:
                    logger.error(f"Channel ID不一致: token={token_aud}, setting={setting_channel_id}")
                    raise jwt.InvalidTokenError(
                        f"Channel ID不一致: トークン={token_aud}, 設定={setting_channel_id}"
                    )
            except Exception as e:
                logger.error(f"トークン解析エラー: {str(e)}")
                raise

            #  token header 情報を取得
            header = jwt.get_unverified_header(id_token)
            kid = header.get('kid')
            alg = header.get('alg', 'RS256')
            logger.info(f"トークンヘッダー情報: kid={kid}, alg={alg}")
            
            if not kid:
                raise jwt.InvalidTokenError('トークンヘッダーにkidがありません')
                
            # 公開鍵を取得
            key = LineKeyManager.get_line_key(kid)
            
            if not key:
                raise jwt.InvalidTokenError('対応する公開鍵が見つかりません')
                
            # 署名を検証してデコードする
            jwk_algorithm = jwt.algorithms.ECAlgorithm if alg == 'ES256' else jwt.algorithms.RSAAlgorithm
            public_key = jwk_algorithm.from_jwk(key)

            decoded = jwt.decode(
                id_token,
                public_key,
                algorithms=[alg],
                audience=setting_channel_id,
                issuer='https://access.line.me'
            )
            # todo オフライン環境でも検証が可能かどうか   issuerパラメータはネットワークリクエストを行わずに、ローカルで妥当性チェックだけします
            # issuer これは LINE プラットフォームの公式認証サーバーアドレスです（トークン発行元）
            # LINE の全ての ID トークンはこのアドレスから発行されています
            # JWT トークンを検証する際、トークンが正規の LINE サーバーから発行されたことを確認する必要があります
            # 発行元を指定しない、または誤って指定した場合、トークンの署名が有効でも不正とみなされます
            # これはセキュリティ対策で、他のサーバーによる偽造トークンを防ぎます

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

    def get_or_create_user(self, line_user_info):
        """LINEユーザー情報から、システムユーザーを取得または作成"""
        from api.user.models import User 
        line_user_id = line_user_info.get('sub')
        
        try:
            with transaction.atomic():
            # 全ての一致するユーザー(削除済みを含む)を検索
                user = User.objects.filter(line_user_id=line_user_id).first()               
                if user:
                    if user.deleted_flag is True:
                        logger.warning(
                            f"削除済みユーザーを検出  - user_id: {user.user_id}, "
                            f"line_user_id: {user.line_user_id}, "
                        )
                    else:
                        logger.info(f"ユーザーを検出: user_id={user.user_id}"
                                    f"line_user_id: {user.line_user_id}, "
                                    )
                        return user
                else:

                    #ユーザーが見つからない場合、新規作成
                    logger.info(f"新規ユーザーを作成: line_user_id={line_user_id}")
                    
                    # LINE情報から基本データを取得
                    email = line_user_info.get('email', None)
                    name = line_user_info.get('name', f'LINE_{line_user_id[:8]}')
                    
                    # 新規ユーザーを作成
                    new_user = User.objects.create(
                        user_id=str(ulid.new()),
                        line_user_id=line_user_id,
                        mail=email,
                        user_name=name,
                        gender='',
                        role=0,
                        phone_number='',
                        deleted_flag=False,
                        created_by=line_user_id,
                        updated_by=line_user_id
                    )
                    
                    logger.info(f"新規ユーザー作成完了: user_id={new_user.user_id}")
                    return new_user
                    
        except Exception as e:
            logger.error(f"ユーザー取得/作成エラー: {str(e)}", exc_info=True)
            raise

    def process_request(self, request):
        """リクエストの認証処理"""
        logger.info(f"===== 認証処理開始 =====")
        logger.info(f"リクエストパス: {request.path}")

        # 認証除外パスの確認
        EXEMPT_PATHS = [ '/api/chat/webhook/']
        if any(request.path.startswith(path) for path in EXEMPT_PATHS):
            logger.info(f"認証除外パス: {request.path}")
            return None

        # Authorization ヘッダーの確認
        auth_header = request.headers.get('Authorization', '')
        logger.info(f"Authorizationヘッダー: {auth_header[:30]}...")

        if not auth_header.startswith('Bearer '):
            logger.error("トークンのフォーマットがBearer フォーマットと一致していません")
            return JsonResponse({'error': '認証が必要です'}, status=401)
        try:
            # トークン検証とユーザー情報取得
            token = auth_header.split(' ')[1]
            auth = LineAuthentication()
            line_user_info = auth.verify_id_token(token)

            if not line_user_info or 'sub' not in line_user_info:
                logger.error("ユーザー情報が不完全です")
                return JsonResponse({'error': 'ユーザー情報が不完全です'}, status=401)

            # システムユーザーの取得または作成
            user = self.get_or_create_user(line_user_info)

            # リクエストにユーザー情報を設定
            request.user_info = user
            logger.info(f"認証成功 request.user_info={request.user_info}")

            
        except Exception as e:
            logger.error(f"認証失敗: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=401)
        
        logger.info("===== 認証処理完了 =====")

