from django.db import models



class Payment(models.Model):
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    method = models.CharField(
        max_length=30,
        choices=[
            ('efectivo', 'Efectivo'),
            ('tarjeta', 'Tarjeta')
        ]
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Pago ${self.amount} – {self.order.order_number}'
