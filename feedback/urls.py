from django.urls import path
from . import views

urlpatterns = [
    path('', views.feedback_form, name='feedback_form'),
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('my-feedback/', views.my_feedback, name='my_feedback'),
    path('success/', views.feedback_success, name='feedback_success'),
]
