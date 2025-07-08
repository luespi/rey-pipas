# apps/messages/models.py
from django.conf import settings
from django.db import models


class Thread(models.Model):
    """
    Un chat 1-a-1 asociado a un pedido (Order).
    Se crea en cuanto cliente u operador abre la pantalla de mensajes.
    """
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="thread",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat pedido #{self.order.pk}"


class Message(models.Model):
    """
    Mensaje dentro de un Thread.
    """
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    text = models.TextField(max_length=2_000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.sender} → {self.text[:30]}..."
