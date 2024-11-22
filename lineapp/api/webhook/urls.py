from django.urls import path

from . import views
urlpatterns = [
    path('payment/status', views.payment_status_webhook, name='payment_status_webhook'),
]
