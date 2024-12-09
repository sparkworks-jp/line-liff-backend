from datetime import datetime, timedelta
import os
import requests
import logging

logger = logging.getLogger(__name__)

class LineKeyManager:
    """LINE公開鍵管理クラス"""
    _keys_cache = {} 
    _last_update = None 
    _cache_duration = timedelta(hours=int(os.getenv('LINE_KEY_CACHE_DURATION_HOURS', 24)))

    @classmethod
    def get_line_key(cls, kid):
        """指定されたkidの公開鍵を取得"""
        try:
            # キャッシュの更新が必要かチェック
            if cls._need_update_cache():
                cls._update_cache()

            # キャッシュから指定したkidの公開鍵を取得
            if kid in cls._keys_cache:
                logger.info(f"キャッシュから公開鍵を取得: {kid}")
                return cls._keys_cache[kid]
            
            # 対応するkidが見つからない場合、キャッシュを更新して再試行
            logger.warning(f"公開鍵が見つかりません。キャッシュを更新します: {kid}")
            cls._update_cache()
            
            if kid in cls._keys_cache:
                return cls._keys_cache[kid]
                
            raise KeyError(f'対応する公開鍵が見つかりません: {kid}')
            
        except Exception as e:
            logger.error(f"公開鍵取得エラー: {str(e)}")
            raise

    @classmethod
    def _need_update_cache(cls):
        """公開鍵キャッシュ有効期限チェック"""
        if not cls._last_update:
            return True
            
        return datetime.now() - cls._last_update > cls._cache_duration

    @classmethod
    def _update_cache(cls):
        """公開鍵キャッシュを更新"""
        try:
            response = requests.get(
                'https://api.line.me/oauth2/v2.1/certs',
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"LINE API エラー: {response.status_code}")
                raise Exception('LINE公開鍵の取得に失敗しました')

            keys_data = response.json()['keys']
            
            # 公開鍵キャッシュを更新
            cls._keys_cache = {key['kid']: key for key in keys_data}
            cls._last_update = datetime.now()
            logger.info(f"公開鍵キャッシュを更新しました。{len(cls._keys_cache)}個の鍵を取得")

            logger.info(f"公開鍵キャッシュを更新しました。{(cls._keys_cache)}個の鍵を取得")
            
        except Exception as e:
            logger.error(f"キャッシュ更新エラー: {str(e)}")
            raise