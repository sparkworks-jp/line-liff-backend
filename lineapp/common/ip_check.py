import os
import logging
from django.http import HttpResponseForbidden
# 从环境变量中加载 PayPay IP 白名单 示例: "203.0.113.0,198.51.100.0"
PAYPAY_IP_WHITELIST = os.getenv("PAYPAY_IP_WHITELIST", "").split(",")

logger = logging.getLogger(__name__)

def ip_whitelist_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        request_ip = get_client_ip(request)
        if request_ip not in PAYPAY_IP_WHITELIST:
            logger.warning(f"Forbidden IP access attempt: {request_ip}")
            return HttpResponseForbidden("Forbidden: IP not allowed")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_client_ip(request):
    """获取请求的 IP 地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip