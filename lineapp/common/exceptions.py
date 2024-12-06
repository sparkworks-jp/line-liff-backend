from rest_framework.exceptions import APIException


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
