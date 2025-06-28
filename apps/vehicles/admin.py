# apps/vehicles/admin.py
from datetime import date

from django.contrib import admin
from django.utils.html import format_html

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Vehículos.
    Ajusta list_display, list_filter, etc. según tu flujo.
    """

    # ----------- Tabla principal -----------
    list_display = (
        "license_plate",
        "brand",
        "model",
        "year",
        "vehicle_type",
        "status_colored",
        "capacity_liters",
        "assigned_operator",
        "needs_maintenance_badge",
        "documents_expired_badge",
    )

    # icono de estado con color
    def status_colored(self, obj):
        palette = {
            "active":         "green",
            "maintenance":    "orange",
            "out_of_service": "red",
            "retired":        "gray",
        }
        color = palette.get(obj.status, "gray")
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Estado"
    status_colored.admin_order_field = "status"

    # indicadores booleanos
    @admin.display(boolean=True, description="Mantenimiento")
    def needs_maintenance_badge(self, obj):
        return obj.needs_maintenance

    @admin.display(boolean=True, description="Docs vencidos")
    def documents_expired_badge(self, obj):
        return obj.documents_expired

    # ----------- Filtros laterales -----------
    list_filter = (
        "status",
        "vehicle_type",
        "year",
        ("next_maintenance", admin.DateFieldListFilter),
        ("registration_expiry", admin.DateFieldListFilter),
        ("insurance_expiry", admin.DateFieldListFilter),
    )

    # ----------- Búsqueda -----------
    search_fields = (
        "license_plate",
        "engine_number",
        "chassis_number",
        "brand",
        "model",
    )

    # ----------- Formulario detallado -----------
    fieldsets = (
        ("Identificación", {
            "fields": (
                ("license_plate", "vehicle_type", "capacity_liters"),
                ("brand", "model", "year"),
                ("engine_number", "chassis_number"),
            )
        }),
        ("Estado / Asignación", {
            "fields": (("status", "assigned_operator"),)
        }),
        ("Documentación", {
            "fields": (
                ("registration_expiry", "insurance_expiry"),
            )
        }),
        ("Mantenimiento", {
            "fields": (
                ("last_maintenance", "next_maintenance"),
                "odometer_reading",
            )
        }),
        ("Ubicación", {
            "classes": ("collapse",),
            "fields": ("current_location",),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("assigned_operator",)
    ordering = ("license_plate",)
    date_hierarchy = "next_maintenance"
