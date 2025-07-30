from django import forms
from .models import Unidad

class UnidadForm(forms.ModelForm):
    class Meta:
        model = Unidad
        # El operador NO selecciona assigned_operator ni status (lo dejamos “activa”)
        exclude = ("assigned_operator", "status")
