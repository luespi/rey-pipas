# apps/payments/admin.py
from django.contrib import admin
from .models import Payment
from django.utils.html import format_html

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "method", "paid_at", "miniatura_comprobante")
    list_filter = ("method", "paid_at")
    search_fields = ("order__order_number", "order__client__email")

    def miniatura_comprobante(self, obj):
        if obj.comprobante:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height: 60px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.2);"/>'
                '</a>',
                obj.comprobante.url,
                obj.comprobante.url,
            )
        return "—"

    miniatura_comprobante.short_description = "Comprobante"
