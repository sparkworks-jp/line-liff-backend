from django.urls import path

from . import views
urlpatterns = [
    path('addresses/list', views.get_address_list, name='get_address_list'),
    path('addresses/add', views.create_address, name='create_address'),
    path('addresses/<str:address_id>/detail', views.get_address_detail, name='get_address'),
    path('addresses/<str:address_id>/delete', views.delete_address, name='delete_address'),
    path('addresses/<str:address_id>/update', views.update_address, name='update_address'),
    path('addresses/<str:address_id>/dafault/set', views.set_default_address, name='set_default_address'),
    path('addresses/default/get', views.get_default_address, name='get_default_address'),
]
