from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('orders/', views.get_order_list, name='get_order_list'),
    path('preview/', views.preview_order, name='preview_order'),
    path('<str:order_id>/', views.get_order_detail, name='get_order_detail'),
    path('cancel/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('delete/<str:order_id>/', views.delete_order, name='delete_order')
]


