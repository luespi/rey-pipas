# apps/orders/urls_payments.py
from django.urls import path
from .views import PaymentCreate, PaymentList

app_name = 'payments'

urlpatterns = [
    path('<int:order_pk>/pagar/', PaymentCreate.as_view(), name='payment-create'),
    path('mis-pagos/',           PaymentList.as_view(),  name='list'),
]
