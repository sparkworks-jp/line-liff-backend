from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('orders/', views.get_order_list, name='get_order_list'),
    path('<str:order_id>/', views.get_order_detail, name='get_order_detail'),
    path('update/<str:order_id>/', views.update_order, name='update_order'),
    path('delete/<str:order_id>/', views.delete_order, name='delete_order'),
]


