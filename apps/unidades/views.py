from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView
from .models import Unidad
from .forms import UnidadForm

class IsOperatorMixin(UserPassesTestMixin):
    """Permite acceso solo a usuarios tipo 'operator'."""
    def test_func(self):
        return getattr(self.request.user, "is_operator", False)

class UnidadCreateView(LoginRequiredMixin, IsOperatorMixin, CreateView):
    model = Unidad
    form_class = UnidadForm
    template_name = "unidades/unidad_form.html"
    success_url = "/dashboard/unidades/"

    def form_valid(self, form):
        # Asignamos automáticamente la unidad al chofer que la crea
        form.instance.assigned_operator = self.request.user
        return super().form_valid(form)

class UnidadListView(LoginRequiredMixin, IsOperatorMixin, ListView):
    template_name = "unidades/unidad_list.html"
    context_object_name = "unidades"

    def get_queryset(self):
        return Unidad.objects.filter(assigned_operator=self.request.user)


from django.views.generic import UpdateView
from .models import Unidad
from .forms import UnidadForm  # si tienes un formulario
from django.urls import reverse_lazy

class UnidadUpdateView(UpdateView):
    model = Unidad
    form_class = UnidadForm
    template_name = "unidades/unidad_form.html"
    success_url = reverse_lazy("unidades:list")  # o el nombre que tengas para regresar
