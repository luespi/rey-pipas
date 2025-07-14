# apps/payments/urls.py
"""
Rutas de la app Payments.

•   Listado de pagos (back‑office)
•   Creación de pago manual desde back‑office
•   Registro de pago por parte del operador (flujo urgente)

No hay rutas duplicadas ni importaciones repetidas.
"""

from django.urls import path
from .views import PaymentListView, PaymentCreateView
from apps.orders.views_operator import OperatorRegisterPaymentView

app_name = "payments"

urlpatterns = [
    # 1) Listado de pagos
    path("", PaymentListView.as_view(), name="list"),

    # 2) Crear pago desde back‑office
    path("create/<int:order_pk>/", PaymentCreateView.as_view(), name="payment-create"),

    # 3) Registrar pago (operador, flujo MVP)
    path(
        "operator/<int:pk>/register/",
        OperatorRegisterPaymentView.as_view(),
        name="operator-register-payment",
    ),
]
