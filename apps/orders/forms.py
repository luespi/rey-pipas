

from django import forms
from .models import Order

BASE = (
    "block w-full rounded-lg border border-gray-300 bg-white "
    "px-4 py-3 text-lg placeholder-gray-400 shadow-sm "
    "focus:border-brand focus:ring-2 focus:ring-brand focus:outline-none transition"
)

from django import forms
from .models import Order, OrderRating

class OrderRequestForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = [
            "quantity_liters",
            "delivery_address",
            "delivery_date",
            "delivery_time_preference",
            "priority",
            "special_instructions",
        ]
        labels = {
            "quantity_liters": "Litros solicitados",
            "delivery_address": "Dirección de entrega",
            "delivery_date": "Fecha de entrega",
            "delivery_time_preference": "Horario preferido",
            "priority": "Prioridad",
            "special_instructions": "Instrucciones especiales",
        }
        widgets = {
            "delivery_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": (
                        "w-full border border-gray-300 rounded-lg px-3 py-2 "
                        "focus:ring-brand focus:border-brand"
                    ),
                }
            ),
        }


class OrderRatingForm(forms.ModelForm):
    class Meta:
        model  = OrderRating
        fields = ["rating", "review"]           # ← SOLO estos dos
        widgets = {
            "rating": forms.RadioSelect(
                choices=[(i, i) for i in range(1, 6)]
            ),
            "review": forms.Textarea(attrs={
                "rows": 3,
                "class": (
                    "w-full border border-gray-300 rounded-lg px-3 py-2 "
                    "focus:ring-brand focus:border-brand"
                ),
            }),
        }



# apps/orders/forms.py  (añade al final)

from apps.payments.models import Payment    # ⬅️ ajusta el import si tu modelo Payment está en otra app

class PaymentForm(forms.ModelForm):
    """Formulario mínimo para registrar pagos en efectivo o tarjeta."""
    class Meta:
        model  = Payment
        fields = ['amount', 'method']
        labels = {
            'amount': 'Monto recibido',
            'method': 'Método',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={
                "class": BASE,
                "step": "0.01",
                "min": "0",
            }),
            'method': forms.Select(attrs={"class": BASE}),
        }
