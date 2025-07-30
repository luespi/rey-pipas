# apps/payments/forms.py
from django import forms
from .models import Payment, PAYMENT_METHODS

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "method", "comprobante")  # 👈 incluye comprobante
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "class": "input"}),
            "method": forms.Select(attrs={"class": "select"}),
        }

    method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.Select(attrs={"class": "select"}))

    # ✅ Campo de imagen para el comprobante
    comprobante = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "file-input"}),
        label="Comprobante (imagen JPG o PNG)",
    )
