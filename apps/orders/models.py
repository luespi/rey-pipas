"""
apps/orders/models.py
Modelo de Pedidos – Rey Pipas PMV
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

#  Relación a la app de unidades
from apps.unidades.models import Unidad


from .constants import ZONES


# ------------------------------------------------------------------------------
#  Modelo principal
# ------------------------------------------------------------------------------
class Order(models.Model):
    # ---------------- Choices ----------------
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pendiente"
        CONFIRMED  = "confirmed",  "Confirmado"
        ASSIGNED   = "assigned",   "Asignado"
        IN_TRANSIT = "in_transit", "En camino"
        DELIVERED  = "delivered",  "Entregado"
        CANCELLED  = "cancelled",  "Cancelado"

    class Priority(models.TextChoices):
        LOW    = "low",    "Baja"
        NORMAL = "normal", "Normal"
        HIGH   = "high",   "Alta"
        URGENT = "urgent", "Urgente"

    # ---------------- Zonas (CDMX + Edoméx) ----------------
    ZONES = [("", "Selecciona tu zona")] + ZONES

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
        null=True, blank=True,
        related_name="assigned_orders",
        limit_choices_to={"user_type": "operator"},
    )
    unidad = models.ForeignKey(
        Unidad,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders",
        verbose_name="Unidad asignada",
    )

    # -------------- Detalles --------------
    quantity_liters = models.PositiveIntegerField(
        validators=[MinValueValidator(500), MaxValueValidator(20_000)]
    )
    delivery_address = models.TextField()

    zone = models.CharField(
        max_length=4,
        choices=ZONES,
        
    )

    colonia = models.CharField("Colonia (opcional)", max_length=120)

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
    assigned_at = models.DateTimeField(null=True, blank=True)      # fecha de asignación
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_confirmation_code = models.CharField(max_length=6, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Precio total del pedido en MXN",
    )

    # ---------------- Meta ----------------
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["operator", "status"]),
            models.Index(fields=["zone", "status"]),
        ]

    # ----------- Métodos utilitarios -----------
    def __str__(self) -> str:
        return f"Pedido {self.order_number} — {self.client.get_full_name()}"

    def _gen_order_number(self) -> str:
        now = timezone.now()
        return f"RP{now:%Y%m%d}{uuid.uuid4().hex[:6].upper()}"


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_status = None

        if not is_new:
            previous_status = Order.objects.get(pk=self.pk).status

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

        # 🔥 Descontar comisión y registrarla si el pedido acaba de cambiar a "Entregado"
        if previous_status != self.Status.DELIVERED and self.status == self.Status.DELIVERED:
            from .models import FondoComision, ComisionDescontada
            try:
                fondo = FondoComision.objects.get(operador=self.operator)
                monto = self.estimated_cost or Decimal("0.00")
                descuento = monto * Decimal("0.10")
                fondo.descontar(descuento)

                # Registrar la comisión descontada solo si no existe aún
                if not hasattr(self, "comision"):
                    ComisionDescontada.objects.create(
                        pedido=self,
                        operador=self.operator,
                        zona=self.zone,
                        monto=descuento
                    )
            except FondoComision.DoesNotExist:
                pass






    
    # ----------- Propiedades -----------
    @property
    def estimated_cost(self):
        if not self.quantity_liters or not self.zone:
            return None
        try:
            from .models import ZonePrice
            price = ZonePrice.objects.get(zone=self.zone).price_per_liter
            return self.quantity_liters * price
        except ZonePrice.DoesNotExist:
            return None


    @property
    def is_overdue(self) -> bool:
        if self.status in {self.Status.DELIVERED, self.Status.CANCELLED}:
            return False
        return timezone.now().date() > self.delivery_date

    @property
    def is_paid(self) -> bool:
        """
        Devuelve True si existe al menos un pago relacionado.
        Soporta tanto el related_name 'payments' como el acceso por defecto 'payment_set'.
        """
        return self.payments.exists() if hasattr(self, "payments") else self.payment_set.exists()

    @property
    def last_payment(self):
        """Devuelve el pago más reciente o None."""
        return self.payments.order_by("-paid_at").first()


# ------------------------------------------------------------------------------
#  Historial de estados
# ------------------------------------------------------------------------------
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

    def __str__(self) -> str:
        return f"{self.order.order_number}: {self.previous_status} → {self.new_status}"


# ------------------------------------------------------------------------------
#  Calificaciones
# ------------------------------------------------------------------------------
class OrderRating(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="rating"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]




# ------------------------------------------------------------------------------
#  Precios por zona
# ------------------------------------------------------------------------------
class ZonePrice(models.Model):
    zone = models.CharField(
        max_length=4,
        choices=Order.ZONES[1:],  # Saltamos el placeholder
        unique=True
    )
    price_per_liter = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Precio por Zona"
        verbose_name_plural = "Precios por Zona"
        ordering = ['zone']

    def __str__(self):
        return f"{self.get_zone_display()}: ${self.price_per_liter}/L"


# ------------------------------------------------------------------------------
#  Fondos de comisión de operadores
# ------------------------------------------------------------------------------
class FondoComision(models.Model):
    operador = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "operator"},
    )
    saldo_actual = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    class Meta:
        verbose_name = "Fondo de Comisión"
        verbose_name_plural = "Fondos de Comisiones"

    def descontar(self, monto):
        self.saldo_actual -= monto
        self.save()

    def __str__(self):
        return f"{self.operador.get_full_name()}: ${self.saldo_actual:,.2f}"


# apps/orders/models.py
class ComisionDescontada(models.Model):
    pedido = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="comision")
    operador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    zona = models.CharField(max_length=4, choices=ZONES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comisión descontada"
        verbose_name_plural = "Comisiones descontadas"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.pedido.order_number} – ${self.monto} – {self.operador.get_full_name()}"
