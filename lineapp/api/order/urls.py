from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('order/<str:order_id>/', views.get_order, name='get_order'),
    path('orderlist/', views.get_order_list, name='get_order_list'),
    path('order/<str:order_id>/', views.update_order, name='update_order'),
    path('order/<str:order_id>/delete/', views.delete_order, name='delete_order'),
]


