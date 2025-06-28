"""
apps/vehicles/models.py
Modelos de vehículos y mantenimiento – Rey Pipas
"""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Vehicle(models.Model):
    """Modelo de vehículos/pipas de agua"""

    # ---------------- Choices ----------------
    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        MAINTENANCE = "maintenance", "En Mantenimiento"
        OUT_OF_SERVICE = "out_of_service", "Fuera de Servicio"
        RETIRED = "retired", "Retirado"

    class VehicleType(models.TextChoices):
        SMALL = "small", "Pequeña (≤ 5 000 L)"
        MEDIUM = "medium", "Mediana (5 000 – 10 000 L)"
        LARGE = "large", "Grande (10 000 – 20 000 L)"
        EXTRA_LARGE = "extra_large", "Extra Grande (> 20 000 L)"

    # -------------- Identificación --------------
    license_plate = models.CharField(
        "Placas", max_length=10, unique=True
    )
    brand = models.CharField("Marca", max_length=50)
    model = models.CharField("Modelo", max_length=50)
    year = models.PositiveSmallIntegerField(
        "Año",
        validators=[MinValueValidator(1990), MaxValueValidator(2030)],
        db_index=True,
    )

    # -------------- Especificaciones --------------
    vehicle_type = models.CharField(
        "Tipo de Vehículo",
        max_length=15,
        choices=VehicleType.choices,
    )
    capacity_liters = models.PositiveIntegerField(
        "Capacidad (Litros)",
        validators=[MinValueValidator(1_000), MaxValueValidator(30_000)],
        db_index=True,
    )

    # -------------- Estado / Asignación --------------
    status = models.CharField(
        "Estado",
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    assigned_operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"user_type": "operator"},
        related_name="assigned_vehicles",
        verbose_name="Operador Asignado",
        db_index=True,
    )

    # -------------- Identificación mecánica --------------
    engine_number = models.CharField(
        "Número de Motor", max_length=50, unique=True, db_index=True
    )
    chassis_number = models.CharField(
        "Número de Chasis", max_length=50, unique=True, db_index=True
    )

    # -------------- Documentación --------------
    registration_expiry = models.DateField("Vencimiento de Registro")
    insurance_expiry = models.DateField("Vencimiento de Seguro")
    last_maintenance = models.DateField(
        "Último Mantenimiento", null=True, blank=True
    )
    next_maintenance = models.DateField(
        "Próximo Mantenimiento", null=True, blank=True
    )

    # -------------- Localización --------------
    current_location = models.CharField(
        "Ubicación Actual", max_length=200, blank=True
    )
    odometer_reading = models.PositiveIntegerField(
        "Kilometraje", default=0
    )

    # -------------- Metadatos --------------
    created_at = models.DateTimeField(
        "Fecha de Registro", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Última Actualización", auto_now=True
    )

    # ---------------- Meta ----------------
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["license_plate"]
        indexes = [
            models.Index(fields=["status", "vehicle_type"]),
            models.Index(fields=["assigned_operator"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["engine_number"], name="unique_engine_number"
            ),
            models.UniqueConstraint(
                fields=["chassis_number"], name="unique_chassis_number"
            ),
        ]

    # -------------- Validaciones extra --------------
    def clean(self):
        """Garantiza coherencia en fechas de mantenimiento."""
        if self.last_maintenance and self.next_maintenance:
            if self.next_maintenance < self.last_maintenance:
                raise ValidationError(
                    "La próxima fecha de mantenimiento debe ser posterior "
                    "al último mantenimiento."
                )

    # -------------- Métodos utilitarios --------------
    def __str__(self):
        return f"{self.license_plate} — {self.brand} {self.model}"

    @property
    def is_available(self) -> bool:
        """¿Está activo y sin bloqueo?"""
        return self.status == self.Status.ACTIVE

    @property
    def needs_maintenance(self) -> bool:
        """¿Fecha próxima de mantenimiento vencida?"""
        return (
            self.next_maintenance
            and timezone.now().date() >= self.next_maintenance
        )

    @property
    def documents_expired(self) -> bool:
        """¿Algún documento vencido?"""
        today = timezone.now().date()
        return self.registration_expiry < today or self.insurance_expiry < today

    @property
    def days_until_next_maintenance(self) -> int | None:
        """Días que faltan para el próximo servicio (None si no hay fecha)."""
        if self.next_maintenance:
            return (self.next_maintenance - timezone.now().date()).days
        return None
