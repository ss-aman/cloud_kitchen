from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_referral, name='generate_referral'),
    path('my-referrals/', views.my_referrals, name='my_referrals'),
    path('api/get-link/', views.get_referral_link, name='get_referral_link'),
]