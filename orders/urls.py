from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_page, name='order_page'),
    path('history/', views.order_history, name='order_history'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
]