from django.urls import path, get_resolver
from . import views


from . import views
urlpatterns = [
    path('create/<str:order_id>/', views.create_payment, name='create_payment')
]