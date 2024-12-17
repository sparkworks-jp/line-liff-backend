from django.urls import path

from . import views
urlpatterns = [
    path('', views.line_webhook, name='line_webhook')
]


