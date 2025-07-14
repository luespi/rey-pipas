# apps/orders/views_operator.py
from __future__ import annotations

from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    DetailView,
    ListView,
    View,
)

from apps.messages.models import Thread
from apps.payments.forms import PaymentForm
from apps.payments.models import Payment
from apps.vehicles.models import Vehicle

from .models import (
    Order,
    OrderRating,
    OrderStatusHistory,
)

# --------------------------------------------------------------------------- #
#  Mixins
# --------------------------------------------------------------------------- #
class OperatorRequiredMixin(UserPassesTestMixin):
    """Restringe las vistas a usuarios con rol «operator»."""

    def test_func(self) -> bool:
        return getattr(self.request.user, "is_operator", False)


# --------------------------------------------------------------------------- #
#  1. Cola de pedidos pendientes
# --------------------------------------------------------------------------- #
class OperatorPendingListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    """Pedidos aún no asignados a ningún operador."""
    template_name = "operator/orders_pending.html"
    context_object_name = "orders"

    def get_queryset(self):
        qs = (
            Order.objects
            .filter(status="pending", operator__isnull=True)
            .select_related("client")
        )

        # Filtro opcional por zona
        zona = self.request.GET.get("zona")
        if zona:
            qs = qs.filter(zone=zona)

        # Filtro opcional por fecha (YYYY‑MM‑DD)
        fecha_str = self.request.GET.get("fecha")
        if fecha_str:
            try:
                qs = qs.filter(delivery_date=date.fromisoformat(fecha_str))
            except ValueError:
                pass  # fecha mal formada → ignorar

        return qs.order_by("zone", "colonia", "delivery_date")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["zonas"] = Order.ZONES
        return ctx


# --------------------------------------------------------------------------- #
#  2. Lista de pedidos asignados (todas las fechas)
# --------------------------------------------------------------------------- #
class OperatorAssignedListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    """Todos los pedidos actualmente asignados al operador."""
    template_name = "operator/orders_assigned.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            Order.objects
            .filter(status="assigned", operator=self.request.user)
            .select_related("thread", "client")
            .order_by("created_at")
        )


# --------------------------------------------------------------------------- #
#  3. Lista de entregas del día
# --------------------------------------------------------------------------- #
class OperatorTodayListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    """Pedidos del día para el operador."""
    template_name = "operator/orders_today.html"
    context_object_name = "orders"

    def get_queryset(self):
        today = timezone.now().date()
        return (
            Order.objects
            .filter(
                operator=self.request.user,
                delivery_date=today,
                status__in=["assigned", "in_transit", "delivered"],
            )
            .order_by("delivery_time_preference", "created_at")
        )


# --------------------------------------------------------------------------- #
#  4. Aceptar pedido
# --------------------------------------------------------------------------- #
class OperatorAcceptOrderView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """El operador toma un pedido pendiente."""
    success_url = reverse_lazy("orders_operator:assigned")

    def post(self, request, pk):
        with transaction.atomic():
            order = (
                Order.objects
                .select_for_update()
                .filter(pk=pk, status="pending", operator__isnull=True)
                .first()
            )
            if not order:
                messages.error(request, "Otro operador ya tomó este pedido.")
                return redirect("orders_operator:pending")

            # Asignar pipa (opcional)
            vehicle = (
                Vehicle.objects
                .filter(assigned_operator=request.user, status="active")
                .first()
            )
            if vehicle:
                order.vehicle = vehicle

            order.operator = request.user
            order.status = "assigned"
            order.assigned_at = timezone.now()
            order.save()

            # Crear hilo de mensajes si no existía
            Thread.objects.get_or_create(order=order)

        messages.success(request, f"Pedido {order.order_number} asignado correctamente.")
        return redirect(self.success_url)


# --------------------------------------------------------------------------- #
#  5. Rechazar (devolver a la cola)
# --------------------------------------------------------------------------- #
class OperatorRejectOrderView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """El operador devuelve a pendientes un pedido ya asignado."""
    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            operator=request.user,
            status="assigned",
        )

        prev_status = order.status
        order.status = "pending"
        order.operator = None
        order.save(update_fields=["status", "operator", "updated_at"])

        OrderStatusHistory.objects.create(
            order=order,
            previous_status=prev_status,
            new_status=order.status,
            changed_by=request.user,
            notes="Rechazado por operador",
        )

        messages.info(request, f"Pedido {order.order_number} devuelto a la cola.")
        return redirect("orders_operator:pending")


# --------------------------------------------------------------------------- #
#  6. Marcar como entregado
# --------------------------------------------------------------------------- #
class OperatorMarkDeliveredView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """El operador confirma la entrega de un pedido asignado."""
    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            operator=request.user,
            status="assigned",
        )

        prev_status = order.status
        order.status = "delivered"
        order.actual_delivery_date = timezone.now()
        order.save(update_fields=["status", "actual_delivery_date", "updated_at"])

        OrderStatusHistory.objects.create(
            order=order,
            previous_status=prev_status,
            new_status=order.status,
            changed_by=request.user,
            notes="Entrega confirmada por operador",
        )

        messages.success(request, f"¡Pedido {order.order_number} marcado como entregado!")
        return redirect("orders_operator:assigned")


# --------------------------------------------------------------------------- #
#  7. Historial de entregas del operador
# --------------------------------------------------------------------------- #
class OperatorHistoryListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    """Histórico de pedidos entregados por el operador."""
    template_name = "operator/orders_history.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        return (
            Order.objects
            .filter(status="delivered", operator=self.request.user)
            .select_related("client")
            .prefetch_related("payments")   # 💡 nuevo
            .order_by("-actual_delivery_date")
        )
    

# --------------------------------------------------------------------------- #
#  8. Detalle de pedido para el operador
# --------------------------------------------------------------------------- #
class OperatorOrderDetailView(LoginRequiredMixin, OperatorRequiredMixin, DetailView):
    """Detalle de un pedido (incluye formulario de registro de pago)."""
    model = Order
    template_name = "operator/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        # El operador solo puede ver su propio pedido (o superusuarios)
        if self.request.user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(operator=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order: Order = ctx["order"]

        # Pago existente (si lo hubiera) y formulario
        existing_payment = Payment.objects.filter(order=order).first()
        ctx["payment"] = existing_payment
        ctx["payment_form"] = PaymentForm(
            initial={
                "amount": existing_payment.amount if existing_payment else order.price,
                "method": existing_payment.method if existing_payment else "",
            }
        )

        # Calificación del cliente (si existe)
        ctx["rating"] = OrderRating.objects.filter(order=order).first()
        return ctx


# --------------------------------------------------------------------------- #
#  9. Registrar / actualizar pago del pedido
# --------------------------------------------------------------------------- #


# apps/orders/views_operator.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View

from apps.orders.models import Order
from apps.payments.models import Payment


# --------------------------------------------------------------------------- #
#  7. Registrar pago (sin formulario)


# --------------------------------------------------------------------------- #
from decimal import Decimal  # al inicio del archivo, junto con los demás imports



from decimal import Decimal  # ya está arriba
# Asegúrate de que PaymentForm esté importado al inicio del archivo:
from apps.payments.forms import PaymentForm


class OperatorRegisterPaymentView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """Permite al operador marcar el pedido como pagado cuando ya está ENTREGADO."""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, operator=request.user)

        # Solo si el pedido ya fue entregado
        if order.status != Order.Status.DELIVERED:
            messages.error(request, "Primero marca el pedido como entregado.")
            return redirect("orders_operator:order-detail", pk=pk)

        # Valida datos del formulario
        form = PaymentForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Revisa los datos del pago.")
            return redirect("orders_operator:order-detail", pk=pk)

        data = form.cleaned_data
        Payment.objects.update_or_create(
            order=order,
            defaults={
                "amount": data["amount"],
                "method": data["method"],
                "paid_at": timezone.now(),
            },
        )

        messages.success(request, "✅ Pago registrado correctamente.")
        return redirect("orders_operator:order-detail", pk=pk)













