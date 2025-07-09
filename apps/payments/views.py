from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView

from .models import Payment
from apps.orders.models import Order


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    fields = ["amount", "method"]          # ajusta a tu modelo real
    template_name = "payments/payment_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.order = Order.objects.get(pk=kwargs["order_id"])
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
