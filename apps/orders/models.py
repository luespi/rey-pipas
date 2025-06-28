"""
apps/orders/models.py
Modelo de Pedidos – Rey Pipas PMV
"""

import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Order(models.Model):
    # ---------------- Choices ----------------
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CONFIRMED = "confirmed", "Confirmado"
        ASSIGNED = "assigned", "Asignado"
        IN_TRANSIT = "in_transit", "En Camino"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Cancelado"

    class Priority(models.TextChoices):
        LOW = "low", "Baja"
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    # -------------- Identificación --------------
    order_number = models.CharField(max_length=20, unique=True)

    # -------------- Relaciones --------------
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        limit_choices_to={"user_type": "client"},
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
        limit_choices_to={"user_type": "operator"},
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # -------------- Detalles --------------
    quantity_liters = models.PositiveIntegerField(
        validators=[MinValueValidator(500), MaxValueValidator(20_000)]
    )
    delivery_address = models.TextField()
    delivery_date = models.DateField()
    delivery_time_preference = models.CharField(max_length=50, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )

    special_instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_confirmation_code = models.CharField(max_length=6, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["operator", "status"]),
        ]

    # ----------- Métodos utilitarios -----------
    def __str__(self):
        return f"Pedido {self.order_number} — {self.client.get_full_name()}"

    def _gen_order_number(self) -> str:
        now = timezone.now()
        return f"RP{now:%Y%m%d}{uuid.uuid4().hex[:6].upper()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            num = self._gen_order_number()
            while Order.objects.filter(order_number=num).exists():
                num = self._gen_order_number()
            self.order_number = num

        if (
            not self.delivery_confirmation_code
            and self.status == self.Status.ASSIGNED
        ):
            self.delivery_confirmation_code = uuid.uuid4().hex[:6].upper()

        super().save(*args, **kwargs)

    # ----------- Propiedades -----------
    @property
    def estimated_cost(self):
        if self.quantity_liters is None:
            return None      # o 0
        # usa tu lógica real de precio
        return self.quantity_liters * self.price_per_liter

    @property
    def is_overdue(self) -> bool:
        if self.status in {self.Status.DELIVERED, self.Status.CANCELLED}:
            return False
        return timezone.now().date() > self.delivery_date


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history"
    )
    previous_status = models.CharField(max_length=20, choices=Order.Status.choices)
    new_status = models.CharField(max_length=20, choices=Order.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.order.order_number}: {self.previous_status} → {self.new_status}"

class OrderRating(models.Model):
    order  = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="rating")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
