from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('webhook/paystack/', views.paystack_webhook, name='paystack-webhook'),
    path('payment/verify/', views.verify_payment_callback, name='verify-payment'),
]
