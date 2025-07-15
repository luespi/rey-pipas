# apps/unidades/models.py
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def unidad_upload_path(instance, filename: str) -> str:
    """
    Todas las imágenes y PDFs quedan en:
        /media/unidades/<uuid>/<nombre_original>
    """
    return f"unidades/{instance.pk or uuid.uuid4()}/{filename}"


# --------------------------------------------------------------------------- #
#  Modelo principal
# --------------------------------------------------------------------------- #
class Unidad(models.Model):
    # ----------------------- Datos técnicos ---------------------------------
    capacidad_litros = models.PositiveIntegerField(
        _("Capacidad del tanque (L)"))
    numero_placas = models.CharField(
        _("Número de placas"), max_length=15, unique=True)

    # ----------------------- Documentación gráfica -------------------------
    foto_frontal      = models.ImageField(_("Foto frontal"), upload_to=unidad_upload_path)
    foto_lateral      = models.ImageField(_("Foto lateral"), upload_to=unidad_upload_path)
    verificacion      = models.ImageField(_("Verificación vehicular"), upload_to=unidad_upload_path)
    tarjeta_circul    = models.ImageField(_("Tarjeta de circulación"), upload_to=unidad_upload_path)
    poliza_seguro     = models.ImageField(_("Póliza de seguro"), upload_to=unidad_upload_path)
    constancia_repuve = models.ImageField(_("Constancia REPUVE"), upload_to=unidad_upload_path)

    # ----------------------- NUEVO: Estado y propietario -------------------
    class Status(models.TextChoices):
        ACTIVE   = "active",  _("Activa")
        INACTIVE = "inactive", _("Inactiva")

    status = models.CharField(
        _("Estado"),
        max_length=8,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    assigned_operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="unidades",
        verbose_name=_("Operador asignado"),
    )

    # ----------------------- Metadatos -------------------------------------
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Unidad")
        verbose_name_plural = _("Unidades")

    # ----------------------- Representación --------------------------------
    def __str__(self) -> str:
        return f"{self.numero_placas} – {self.capacidad_litros} L"
