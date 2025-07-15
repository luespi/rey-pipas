# apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Order,
    OrderStatusHistory,
    OrderRating,
)

# ────────────────────────────────────────────────────────────────────────────
#  INLINES
# ────────────────────────────────────────────────────────────────────────────
class OrderStatusHistoryInline(admin.TabularInline):
    """Historial de cambios de estado dentro de la orden."""
    model = OrderStatusHistory
    extra = 0
    fields = ("timestamp", "previous_status", "new_status", "changed_by", "notes")
    readonly_fields = ("timestamp",)
    show_change_link = True


class OrderRatingInline(admin.StackedInline):
    """Calificación del cliente."""
    model = OrderRating
    extra = 0
    max_num = 1


# ────────────────────────────────────────────────────────────────────────────
#  ADMIN PRINCIPAL
# ────────────────────────────────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Configuración del modelo Order en el sitio de administración.
    Ahora usa el campo «unidad» en lugar de «vehicle».
    """

    # --- Tabla principal ---
    list_display = (
        "order_number",
        "client",
        "operator",
        "unidad",              # ← NUEVO  (muestra la FK)
        "zone_label",
        "status_colored",
        "priority",
        "quantity_liters",
        "delivery_date",
        "created_at",
    )

    def zone_label(self, obj):
        return obj.get_zone_display() or "—"
    zone_label.short_description = "Zona"
    zone_label.admin_order_field = "zone"

    def status_colored(self, obj):
        color = {
            "pending":    "gray",
            "confirmed":  "blue",
            "assigned":   "indigo",
            "in_transit": "orange",
            "delivered":  "green",
            "cancelled":  "red",
        }.get(obj.status, "gray")
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_colored.short_description = "Estado"
    status_colored.admin_order_field = "status"

    # --- Filtros laterales ---
    list_filter = (
        "zone",
        "status",
        "priority",
        "delivery_date",
        "created_at",
    )

    # --- Búsqueda ---
    search_fields = (
        "order_number",
        "client__username",
        "operator__username",
        "unidad__numero_placas",
        "delivery_address",
        "colonia",
    )

    # --- Vista detallada ---
    fieldsets = (
        ("Identificación", {
            "fields": ("order_number", "status", "priority")
        }),
        ("Relaciones", {
            "fields": ("client", "operator", "unidad")   # ← 'unidad' sustituye a 'vehicle'
        }),
        ("Detalle de entrega", {
            "fields": (
                ("zone", "colonia"),
                ("quantity_liters", "estimated_cost"),
                "delivery_address",
                ("delivery_date", "delivery_time_preference"),
                ("actual_delivery_date", "delivery_confirmation_code"),
            )
        }),
        ("Notas", {
            "classes": ("collapse",),
            "fields": ("special_instructions", "notes")
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at")
        }),
    )

    readonly_fields     = ("estimated_cost", "created_at", "updated_at")
    autocomplete_fields = ("client", "operator", "unidad")  # ← actualizado
    date_hierarchy      = "delivery_date"
    ordering            = ("-created_at",)
    inlines             = [OrderStatusHistoryInline, OrderRatingInline]


# ────────────────────────────────────────────────────────────────────────────
#  MODELOS RELACIONADOS
# ────────────────────────────────────────────────────────────────────────────
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display  = ("order", "previous_status", "new_status", "timestamp", "changed_by")
    list_filter   = ("previous_status", "new_status", "timestamp")
    search_fields = ("order__order_number", "changed_by__username")
    readonly_fields = ("timestamp",)


@admin.register(OrderRating)
class OrderRatingAdmin(admin.ModelAdmin):
    list_display  = ("order", "rating", "created_at")
    list_filter   = ("rating", "created_at")
    search_fields = ("order__order_number",)
    readonly_fields = ("created_at",)
