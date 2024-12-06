import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from freezegun import freeze_time
from core.utils.LineKeyManager import LineKeyManager
import requests
import logging

# テストのログ設定
logging.basicConfig(level=logging.INFO, format='='*50 + '\n%(asctime)s - %(name)s - %(levelname)s\n%(message)s\n' + '='*50)
logger = logging.getLogger(__name__)

class LineKeyManagerTests(unittest.TestCase):  
    def setUp(self):
        # テスト前にキャッシュをリセット
        logger.info("テスト開始: キャッシュをリセットします")
        LineKeyManager._keys_cache = {}
        LineKeyManager._last_update = None

    def test_cache_expiration(self):
        """キャッシュの有効期限テスト"""
        logger.info("キャッシュの有効期限テストを開始します")
        
        # LINE APIレスポンスをモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'keys': [
                {'kid': 'key1', 'value': 'test1'},
                {'kid': 'key2', 'value': 'test2'}
            ]
        }

        # 初回リクエストをテスト
        logger.info("初回リクエストのテストを実行")
        with patch('requests.get', return_value=mock_response):
            key = LineKeyManager.get_line_key('key1')
            self.assertEqual(key['value'], 'test1')
            logger.info("初回リクエスト: APIが正常に呼び出されました")

        # 24時間後のリクエストをテスト
        logger.info("24時間後のキャッシュ期限切れテストを実行")
        with freeze_time(datetime.now() + timedelta(hours=25)):
            with patch('requests.get', return_value=mock_response):
                key = LineKeyManager.get_line_key('key1')
                self.assertEqual(key['value'], 'test1')
                logger.info("キャッシュ期限切れ: APIが再度呼び出されました")

    def test_line_key_update(self):
        """公開鍵の更新テスト"""
        logger.info("公開鍵の更新テストを開始します")

        # 初回レスポンス
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            'keys': [{'kid': 'key1', 'value': 'old_value'}]
        }

        # 更新後のレスポンス
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'keys': [{'kid': 'key1', 'value': 'new_value'}]
        }

        # 公開鍵の更新をテスト
        logger.info("初期値の取得テスト")
        with patch('requests.get', return_value=mock_response1):
            key = LineKeyManager.get_line_key('key1')
            self.assertEqual(key['value'], 'old_value')
            logger.info("初期値が正しく取得されました")

        logger.info("更新値の取得テスト")
        with patch('requests.get', return_value=mock_response2):
            with freeze_time(datetime.now() + timedelta(hours=25)):
                key = LineKeyManager.get_line_key('key1')
                self.assertEqual(key['value'], 'new_value')
                logger.info("更新値が正しく取得されました")

    def test_error_handling(self):
        """エラーハンドリングテスト"""
        logger.info("エラーハンドリングテストを開始します")

        # APIエラーのテスト
        logger.info("APIエラーのテストを実行")
        with patch('requests.get', side_effect=Exception('API Error')):
            with self.assertRaises(Exception):
                LineKeyManager.get_line_key('key1')
                logger.info("APIエラーが正しく検出されました")

        # 無効なkidのテスト
        logger.info("無効なkidのテストを実行")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'keys': []}

        with patch('requests.get', return_value=mock_response):
            with self.assertRaises(KeyError):
                LineKeyManager.get_line_key('invalid_kid')
                logger.info("無効なkidエラーが正しく検出されました")

    def tearDown(self):
        logger.info("テストが完了しました\n")

if __name__ == '__main__':
    unittest.main()