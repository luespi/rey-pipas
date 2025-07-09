

from django import forms
from .models import Order

BASE = (
    "block w-full rounded-lg border border-gray-300 bg-white "
    "px-4 py-3 text-lg placeholder-gray-400 shadow-sm "
    "focus:border-brand focus:ring-2 focus:ring-brand focus:outline-none transition"
)

from django import forms
from .models import Order, OrderRating

# orders/forms.py
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Order


BASE_INPUT_CSS = (
    "w-full border border-gray-300 rounded-lg px-3 py-2 "
    "focus:ring-brand focus:border-brand"
)
from datetime import date
from django import forms
from django.core.exceptions import ValidationError

from .models import Order


BASE_INPUT_CSS = (
    "w-full border border-gray-300 rounded-lg px-3 py-2 "
    "focus:ring-brand focus:border-brand"
)


class OrderRequestForm(forms.ModelForm):
    """Formulario de creación de pedidos con zona y colonia."""

    class Meta:
        model = Order
        fields = [
            "zone",
            "colonia",             # ← NUEVO
            "quantity_liters",
            "delivery_address",
            "delivery_date",
            "delivery_time_preference",
            "priority",
            "special_instructions",
        ]
        labels = {
            "zone": "Zona (alcaldía o municipio)",
            "colonia": "Colonia",
            "quantity_liters": "Litros solicitados",
            "delivery_address": "Dirección de entrega",
            "delivery_date": "Fecha de entrega",
            "delivery_time_preference": "Horario preferido",
            "priority": "Prioridad",
            "special_instructions": "Instrucciones especiales",
        }
        help_texts = {
            "zone": "Selecciona tu zona antes de continuar.",
            "colonia": "Ej. Del Valle, Centro, Evolución…",
            "delivery_time_preference": "Ej. 8 am – 12 pm",
        }
        widgets = {
            "zone": forms.Select(attrs={"class": BASE_INPUT_CSS}),
            "colonia": forms.TextInput(attrs={"class": BASE_INPUT_CSS}),  # ← NUEVO
            "quantity_liters": forms.NumberInput(attrs={"class": BASE_INPUT_CSS}),
            "delivery_address": forms.Textarea(
                attrs={"rows": 2, "class": BASE_INPUT_CSS}
            ),
            "delivery_date": forms.DateInput(
                attrs={"type": "date", "class": BASE_INPUT_CSS}
            ),
            "delivery_time_preference": forms.TextInput(
                attrs={"placeholder": "Mañana / Tarde", "class": BASE_INPUT_CSS}
            ),
            "priority": forms.Select(attrs={"class": BASE_INPUT_CSS}),
            "special_instructions": forms.Textarea(
                attrs={"rows": 3, "class": BASE_INPUT_CSS}
            ),
        }

    # -------- Validaciones adicionales --------

    def clean_zone(self):
        """Evita que el usuario deje la opción placeholder vacía."""
        zone = self.cleaned_data["zone"]
        if zone == "":
            raise ValidationError("Debes seleccionar una zona válida.")
        return zone

    def clean_delivery_date(self):
        """Impide escoger fechas pasadas."""
        d = self.cleaned_data["delivery_date"]
        if d < date.today():
            raise ValidationError("La fecha de entrega no puede estar en el pasado.")
        return d




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
