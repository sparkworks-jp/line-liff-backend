from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.CreateOrderView.as_view(), name='create_order'),       
    path('<str:order_id>/', views.OrderDetailView.as_view(), name='order_detail'), 
    path('list/', views.OrderListView.as_view(), name='order_list'),        
]


