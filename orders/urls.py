from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_page, name='order_page'),
    path('place-order/', views.place_order, name='place_order'),
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('history/', views.order_history, name='order_history'),
    path('current/', views.current_orders, name='current_orders'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('confirm-payment/<int:order_id>/', views.confirm_payment, name='confirm_payment'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
]