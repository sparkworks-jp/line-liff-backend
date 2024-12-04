from django.urls import path

from . import views
urlpatterns = [
    path('payment/status', views.payment_status_webhook, name='payment_status_webhook'),
    path('openai/function', views.openai_function_test, name='openai_function_test'),
]
