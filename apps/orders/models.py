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
    ZONES = [
        ("",  "Selecciona tu zona"),  # placeholder no válido
        # ── Alcaldías ─────────────────────
        ("AO", "Álvaro Obregón"), ("AZ", "Azcapotzalco"), ("BJ", "Benito Juárez"),
        ("CO", "Coyoacán"), ("CU", "Cuauhtémoc"), ("CJ", "Cuajimalpa de Morelos"),
        ("GA", "Gustavo A. Madero"), ("IZ", "Iztacalco"), ("IH", "Iztapalapa"),
        ("MC", "Magdalena Contreras"), ("MI", "Miguel Hidalgo"), ("MA", "Milpa Alta"),
        ("TL", "Tláhuac"), ("TM", "Tlalpan"), ("VC", "Venustiano Carranza"),
        ("XO", "Xochimilco"),
        # ── Municipios conurbados ────────
        ("ACO", "Acolman"), ("AME", "Amecameca"), ("APA", "Apaxco"),
        ("ATC", "Atenco"), ("ATL", "Atizapán de Zaragoza"), ("CAP", "Capulhuac"),
        ("CHI", "Chicoloapan"), ("CHT", "Chimalhuacán"), ("CJC", "Coacalco de Berriozábal"),
        ("CME", "Cuautitlán México"), ("CIZ", "Cuautitlán Izcalli"),
        ("ECT", "Ecatepec de Morelos"), ("HIX", "Huehuetoca"), ("HZN", "Hueypoxtla"),
        ("IZC", "Ixtapaluca"), ("JAL", "Jaltenco"), ("LNE", "La Paz"), ("LCO", "Lerma"),
        ("MEL", "Melchor Ocampo"), ("NZA", "Nezahualcóyotl"), ("NIC", "Nicolás Romero"),
        ("NUP", "Nopaltepec"), ("OTU", "Otumba"), ("PAP", "Papalotla"),
        ("SLM", "San Martín de las Pirámides"), ("SFE", "San Felipe del Progreso"),
        ("SFS", "San Francisco Soyaniquilpan"), ("SOX", "Santo Tomás"),
        ("TEC", "Tecámac"), ("TEM", "Temamatla"), ("TEN", "Tenango del Aire"),
        ("TEO", "Teoloyucan"), ("TEX", "Texcoco"), ("TLA", "Tlalnepantla de Baz"),
        ("TLN", "Tepotzotlán"), ("TNT", "Teotihuacán"), ("TUL", "Tultitlán"),
        ("VCS", "Valle de Chalco Solidaridad"), ("ZMP", "Zumpango"),
    ]

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
        "Zona (alcaldía o municipio)",
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
        """Ejemplo de cálculo; ajusta según tu lógica de precios."""
        if self.quantity_liters is None:
            return None
        return self.quantity_liters * self.price_per_liter  # `price_per_liter` definido en servicios

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
