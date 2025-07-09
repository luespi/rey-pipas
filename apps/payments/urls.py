# apps/payments/urls.py
from django.urls import path
from .views import PaymentCreateView

app_name = "payments"

urlpatterns = [
    path(
        "create/<int:order_id>/",
        PaymentCreateView.as_view(),
        name="create",
    ),
]
