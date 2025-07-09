# apps/payments/urls.py
from django.urls import path
from .views import PaymentCreateView
from django.urls import path
from .views import PaymentListView, PaymentCreateView

app_name = "payments"

urlpatterns = [
    path("", PaymentListView.as_view(), name="list"),
    path("create/<int:order_pk>/", PaymentCreateView.as_view(), name="payment-create"),
    path(
        "create/<int:order_id>/",
        PaymentCreateView.as_view(),
        name="create",
    ),
]

