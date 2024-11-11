# urls.py

from django.urls import path
from . import views

urlpatterns = [
    # path('product/', views.create_product, name='create_product'),
    path('product/<str:product_id>/', views.get_product, name='get_product'),
    path('products/', views.list_products, name='list_products'),
    # path('product/<str:product_id>/update/', views.update_product, name='update_product'),
    # path('product/<str:product_id>/delete/', views.delete_product, name='delete_product'),
]
