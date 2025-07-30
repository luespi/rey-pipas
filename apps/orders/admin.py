# apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Order,
    OrderStatusHistory,
    OrderRating,
)


from .models import (
    Order,
    OrderStatusHistory,
    OrderRating,
    ZonePrice,
    FondoComision,  # ← AGREGA ESTO
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
        "estimated_cost_display",  # ← aquí lo agregas
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





    def estimated_cost_display(self, obj):
        cost = obj.estimated_cost
        try:
            return f"${float(cost):,.2f}"
        except (TypeError, ValueError):
            return "—"

    estimated_cost_display.short_description = "Costo estimado"
    estimated_cost_display.admin_order_field = "price"


    def get_readonly_fields(self, request, obj=None):
            if request.user.groups.filter(name='owner').exists():
                # Deja sólo status editable para el grupo owner
                todos = [f.name for f in self.model._meta.fields]
                return [f for f in todos if f != 'status'] + list(self.readonly_fields or [])
            return self.readonly_fields

    
    def has_add_permission(self, request):
        # Solo superusers pueden agregar pedidos
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusers pueden borrar pedidos
        return request.user.is_superuser
    


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



from .models import ZonePrice

@admin.register(ZonePrice)
class ZonePriceAdmin(admin.ModelAdmin):
    list_display = ['zone', 'price_per_liter', 'updated_at']
    list_editable = ['price_per_liter']
    search_fields = ['zone']



@admin.register(FondoComision)
class FondoComisionAdmin(admin.ModelAdmin):
    list_display = ['operador', 'saldo_actual']



from .models import ComisionDescontada

from django.db.models import Sum
from django.utils.html import format_html
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import ComisionDescontada

from django.contrib import admin, messages
from django.db.models import Sum
from .models import ComisionDescontada

@admin.register(ComisionDescontada)
class ComisionDescontadaAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'operador', 'zona', 'monto', 'fecha']
    list_filter = ['zona', 'operador', ('fecha', admin.DateFieldListFilter)]
    search_fields = ['pedido__order_number', 'operador__email', 'operador__first_name', 'operador__last_name']
    ordering = ['-fecha']

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            qs = response.context_data['cl'].queryset
            total = qs.aggregate(Sum('monto'))['monto__sum'] or 0
            formatted = "${:,.2f}".format(float(total))

            self.message_user(
                request,
                message=f"💰 Total de comisiones en esta vista: {formatted}",
                level=messages.INFO
            )
        except Exception as e:
            self.message_user(request, f"Error calculando el total: {str(e)}", level=messages.WARNING)

        return response
