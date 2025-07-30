# apps/unidades/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Unidad


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = (
        "miniatura_frontal",
        "miniatura_lateral",
        "numero_placas",
        "capacidad_litros",
        "creado",
        "actualizado",
    )
    list_display_links = ("numero_placas",)
    list_filter = ("creado",)
    search_fields = ("numero_placas",)
    ordering = ("-creado",)

    readonly_fields = (
        "creado",
        "actualizado",
        "preview_frontal",
        "preview_lateral",
        "preview_verificacion",
        "preview_tarjeta",
        "preview_poliza",
        "preview_repuve",
    )

    fieldsets = (
        (None, {
            "fields": (
                "numero_placas",
                "capacidad_litros",
            )
        }),
        ("Documentación e imágenes", {
            "fields": (
                "preview_frontal",
                "foto_frontal",
                "preview_lateral",
                "foto_lateral",
                "preview_verificacion",
                "verificacion",
                "preview_tarjeta",
                "tarjeta_circul",
                "preview_poliza",
                "poliza_seguro",
                "preview_repuve",
                "constancia_repuve",
            )
        }),
        ("Metadatos", {
            "fields": ("creado", "actualizado"),
        }),
    )

    # ---- MINIATURAS EN LISTA (solo frontal y lateral por ahora) ------------
    def miniatura_frontal(self, obj):
        if obj.foto_frontal and hasattr(obj.foto_frontal, "url"):
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="height:50px; object-fit:cover; border-radius:4px;" /></a>',
                obj.foto_frontal.url
            )
        return "-"
    miniatura_frontal.short_description = "Frontal"

    def miniatura_lateral(self, obj):
        if obj.foto_lateral and hasattr(obj.foto_lateral, "url"):
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="height:50px; object-fit:cover; border-radius:4px;" /></a>',
                obj.foto_lateral.url
            )
        return "-"
    miniatura_lateral.short_description = "Lateral"

    # ---- VISTAS PREVIAS EN FORMULARIO --------------------------------------
    def preview_frontal(self, obj):
        return self._preview_image(obj.foto_frontal, "Frontal")

    def preview_lateral(self, obj):
        return self._preview_image(obj.foto_lateral, "Lateral")

    def preview_verificacion(self, obj):
        return self._preview_image(obj.verificacion, "Verificación")

    def preview_tarjeta(self, obj):
        return self._preview_image(obj.tarjeta_circul, "Tarjeta circulación")

    def preview_poliza(self, obj):
        return self._preview_image(obj.poliza_seguro, "Póliza")

    def preview_repuve(self, obj):
        return self._preview_image(obj.constancia_repuve, "REPUVE")

    def _preview_image(self, image_field, label):
        if image_field and hasattr(image_field, "url"):
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="height:120px; object-fit:cover; border-radius:6px;" /></a>',
                image_field.url
            )
        return f"No hay imagen de {label}"
