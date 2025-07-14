# apps/payments/models.py
from django.db import models

# 💡 NUEVO — declara lista central de métodos
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

    # ⇣ usa la lista recién creada
    method = models.CharField(max_length=15, choices=PAYMENT_METHODS)

    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Pago ${self.amount} – {self.order.order_number}"
