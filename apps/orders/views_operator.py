# apps/orders/views_operator.py

from .models import Order, OrderStatusHistory    # ← añade OrderStatusHistory

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, View

from .models import Order
from apps.vehicles.models import Vehicle
from apps.messages.models import Thread


class OperatorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_operator


class OperatorPendingListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    template_name = "operator/orders_pending.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(status="pending").order_by("created_at")


class OperatorAssignedListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    template_name = "operator/orders_assigned.html"
    context_object_name = "orders"

    def get_queryset(self):
            return (
                Order.objects
                .filter(status="assigned", operator=self.request.user)
                .select_related("thread", "client")
                .order_by("created_at")
            )


class OperatorAcceptOrderView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """
    POST-only endpoint para aceptar un pedido.
    """

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, status="pending")

        # vehículo activo del operador
        vehicle = (
            Vehicle.objects.filter(
                assigned_operator=request.user, status="active"
            ).first()
        )
        if vehicle is None:
            messages.error(
                request,
                "No tienes una pipa activa asignada. Contacta a un administrador.",
            )
            return redirect("orders_operator:pending")

        with transaction.atomic():
            order.operator = request.user
            order.vehicle = vehicle
            order.status = "assigned"
            order.assigned_at = timezone.now()
            order.save()

            # crea hilo de chat si no existe
            Thread.objects.get_or_create(order=order)

        messages.success(request, f"Pedido #{order.id} asignado correctamente.")
        return redirect("orders_operator:assigned")


class OperatorRejectOrderView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """Devuelve un pedido a la cola."""
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, operator=request.user, status="assigned")

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

        messages.info(request, f"Pedido #{order.id} devuelto a la cola.")
        return redirect("orders_operator:pending")


class OperatorMarkDeliveredView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """Marca el pedido como entregado."""
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, operator=request.user, status="assigned")

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

        messages.success(request, f"¡Pedido #{order.id} marcado como entregado!")
        return redirect("orders_operator:assigned")