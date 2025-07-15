# apps/unidades/admin.py
from django.contrib import admin
from .models import Unidad


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    # ---- LISTA (changelist) -------------------------------------------------
    # Columnas que aparecerán en /admin/unidades/unidad/
    list_display = (
        "numero_placas",
        "capacidad_litros",
        "creado",
        "actualizado",
    )
    list_display_links = ("numero_placas",)      # Solo placas será enlace al detalle
    list_filter = ("creado",)                    # Filtro lateral por fecha de creación
    search_fields = ("numero_placas",)           # Búsqueda rápida por placas
    ordering = ("-creado",)                      # Más reciente primero

    # ---- FORMULARIO ---------------------------------------------------------
    readonly_fields = ("creado", "actualizado")  # Campos solo‑lectura en el detalle

    fieldsets = (
        (None, {
            "fields": (
                "numero_placas",
                "capacidad_litros",
            )
        }),
        ("Documentación e imágenes", {
            "fields": (
                "foto_frontal",
                "foto_lateral",
                "verificacion",
                "tarjeta_circul",
                "poliza_seguro",
                "constancia_repuve",
            )
        }),
        ("Metadatos", {
            "fields": ("creado", "actualizado"),
        }),
    )

    # ---- OPTATIVO: mini‑preview de imágenes en la lista ---------------------
    # Descomenta si quieres ver la foto frontal como thumbnail en list_display
    #
    # from django.utils.html import format_html
    #
    # def mini_foto(self, obj):
    #     if obj.foto_frontal:
    #         return format_html('<img src="{}" style="height:45px;" />', obj.foto_frontal.url)
    #     return "-"
    # mini_foto.short_description = "Vista"
    #
    # list_display = ("mini_foto",) + list_display
