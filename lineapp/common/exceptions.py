import logging
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

class CustomAPIException(APIException):
    """カスタム例外"""

    def __init__(self, status, message=None, code=None, severity=None):
        self.status_code = status
        if message is None:
            message = '例外が発生しました。'
        if code is None:
            code = 'API Exception'
        if severity is None:
            severity = 'error'
        detail = {
            'message': message,
            'severity': severity
        }
        super().__init__(detail=detail, code=code)

def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)
    
    request = context.get('request', None)
    view = context.get('view', None)
    view_name = view.__class__.__name__ if view else '不明なビュー'
    
    if isinstance(exc, CustomAPIException):
        # カスタム例外の処理
        logger.warning(
            f"{view_name}でカスタム例外が発生: {exc.detail.get('message')}",
            extra={
                'status_code': exc.status_code,
                'view': view_name,
                'path': request.path if request else '不明',
                'method': request.method if request else '不明'
            }
        )
        return Response(
            exc.detail,
            status=exc.status_code
        )
    
    # elif response is not None:
    #     # DRF標準例外の処理
    #     logger.error(
    #         f"{view_name}でDRF例外が発生: {str(exc)}",
    #         extra={
    #             'status_code': response.status_code,
    #             'view': view_name,
    #             'path': request.path if request else '不明',
    #             'method': request.method if request else '不明'
    #         }
    #     )
    #     return Response({
    #         'status': 'エラー',
    #         'message': str(exc),
    #         'severity': 'エラー'
    #     }, status=response.status_code)
    
    else:
        # 未捕捉の例外処理
        logger.error(
            f"{view_name}で未処理の例外が発生: {str(exc)}",
            exc_info=True,
            extra={
                'view': view_name,
                'path': request.path if request else '不明',
                'method': request.method if request else '不明'
            }
        )
        return Response({
            'status': 'エラー',
            'message': 'システムエラーが発生しました',
            'severity': 'エラー'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

