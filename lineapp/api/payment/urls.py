from django.urls import path

from . import views
urlpatterns = [
    path('create/<str:order_id>', views.create_payment, name='create_payment')
]
