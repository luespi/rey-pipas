# apps/payments/forms.py
from django import forms
from .models import Payment, PAYMENT_METHODS

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "method")
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "class": "input"}),
            "method": forms.Select(attrs={"class": "select"}),
        }

    # Asegura que el select muestre los tres métodos
    method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.Select(attrs={"class": "select"}))
