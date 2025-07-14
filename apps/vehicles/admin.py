# apps/vehicles/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # ──────────── listado ─────────────
    list_display = (
        "plate_number",
        "assigned_operator",
        "capacity_litres",
        "created_at",
        "preview_front",
    )
    ordering      = ("plate_number",)
    list_filter   = ("created_at",)
    search_fields = ("plate_number", "assigned_operator__email", "assigned_operator__username")

    # ──────────── detalle ─────────────
    readonly_fields = ("preview_front", "created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("assigned_operator", "plate_number", "capacity_litres")
        }),
        ("Fotos / documentos", {
            "fields": (
                "photo_front", "photo_side",
                "photo_verificacion", "photo_tarjeta_circulacion",
                "photo_poliza_seguro", "photo_constancia_repuve",
            )
        }),
        ("Tiempos", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # ──────────── utilidades ──────────
    def preview_front(self, obj):
        if obj.photo_front:
            return format_html('<img src="{}" style="height:120px;">', obj.photo_front.url)
        return "—"
    preview_front.short_description = "Vista previa"
