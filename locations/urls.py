from django.urls import path
from . import views

urlpatterns = [
    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('addresses/get/', views.get_user_addresses, name='get_user_addresses'),
]