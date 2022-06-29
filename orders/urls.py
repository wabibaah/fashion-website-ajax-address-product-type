from django.urls import path
from . import views


urlpatterns = [
  path('place_order/', views.place_order, name='place_order'),
  path('paystack-payment/', views.paystackPayment, name='paystack-payment'),
  path('webhook/', views.webhook, name='webhook'),
  path('payments/', views.payments, name='payments'),
  path('payment-confirm', views.paymentConfirm, name='payment-confirm'),
  path('order_complete/', views.order_complete, name='order_complete'),
]