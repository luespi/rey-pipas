# apps/payments/models.py
from django.db import models

PAYMENT_METHODS = [
    ("efectivo", "Efectivo"),
    ("transferencia", "Transferencia bancaria"),
    ("oxxo", "OXXO"),
]

class Payment(models.Model):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    paid_at = models.DateTimeField(auto_now_add=True)

    # ✅ Nuevo campo para subir comprobante
    comprobante = models.ImageField(
        upload_to="comprobantes_pagos/",
        blank=True,
        null=True,
        help_text="Sube el comprobante si el pago fue por transferencia u OXXO.",
    )

    def __str__(self) -> str:
        return f"Pago ${self.amount} – {self.order.order_number}"
