# apps/vehicles/models.py
from django.conf import settings          # ← en vez de importar User
from django.db import models
from django_resized import ResizedImageField

class Vehicle(models.Model):
    assigned_operator = models.OneToOneField(
        settings.AUTH_USER_MODEL,         # ← referencia perezosa
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "operator"},  # literal evita el import
        related_name="vehicle",
        verbose_name="Operador",
    )

    capacity_litres = models.PositiveIntegerField("Capacidad del tanque (L)")
    plate_number    = models.CharField("Número de placas", max_length=10, unique=True)
   

    # … (resto de campos de fotos idénticos) …

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        # assigned_operator ya es instancia de User en tiempo de ejecución
        return f"{self.plate_number} · {self.assigned_operator.get_full_name()}"
