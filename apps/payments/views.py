#  views.py de  app payments

from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView

from .models import Payment
from apps.orders.models import Order

# apps/payments/views.py
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .models import Payment
from .forms import PaymentForm
from apps.orders.models import Order

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm  # 👈 Usa el formulario con comprobante
    template_name = "payments/payment_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.order = Order.objects.get(pk=kwargs["order_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.order = self.order
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("orders:orders_operator:history")


from django.views.generic import ListView
from .models import Payment
from django.contrib.auth.mixins import LoginRequiredMixin

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payments/payment_list.html"
    context_object_name = "payments"

    def get_queryset(self):
        return Payment.objects.filter(order__client=self.request.user)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views import View

from apps.orders.models import Order
from .models import Payment
from .forms import PaymentForm






#comentada
"""

#class #OperatorRegisterPaymentView#(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        # Seguridad: si NO está entregado, regresa al detalle
        if order.status != "delivered":
            return redirect("orders_operator:order-detail", pk=pk)

        form = PaymentForm(request.POST)
        if form.is_valid():
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "amount": form.cleaned_data["amount"],
                    "method": form.cleaned_data["method"],
                    "paid_at": timezone.now(),
                },
            )

        # Redirección final al mismo detalle
        return redirect("orders_operator:order-detail", pk=pk)




"""






