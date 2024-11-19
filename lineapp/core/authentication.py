from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.http import HttpRequest
import logging

logger = logging.getLogger(__name__)
#  DRF認証クラス　DRF只做最基本的状态确认
class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None 
            
        try:
            if hasattr(request._request, 'user'):
                user = request._request.user
                if not user.deleted_flag:  
                    return (user, None)
            return None
            
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')

    def authenticate_header(self, request):
        return 'Bearer'