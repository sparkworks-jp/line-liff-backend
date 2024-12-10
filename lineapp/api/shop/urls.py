# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.list_products, name='list_products')
]
