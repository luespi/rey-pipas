# apps/orders/views_operator.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, View

from .models import Order, OrderStatusHistory
from apps.vehicles.models import Vehicle
from apps.messages.models import Thread


# --------------------------------------------------------------------------- #
#  Mixins
# --------------------------------------------------------------------------- #
class OperatorRequiredMixin(UserPassesTestMixin):
    """Restringe las vistas a usuarios con rol 'operator'."""
    def test_func(self):
        return getattr(self.request.user, "is_operator", False)


# --------------------------------------------------------------------------- #
#  1. Cola de pedidos pendientes
# --------------------------------------------------------------------------- #
from datetime import date
        # …importaciones que ya tienes…
from django.views.generic import ListView

        # --------------------------------------------------------------------------- #
        #  1. Cola de pedidos pendientes
        # --------------------------------------------------------------------------- #
class OperatorPendingListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
            template_name = "operator/orders_pending.html"
            context_object_name = "orders"

            def get_queryset(self):
                qs = (
                    Order.objects
                    .filter(status="pending", operator__isnull=True)
                    .select_related("client")
                )

                # ---------------- Filtro por ZONA ----------------
                zona = self.request.GET.get("zona")
                if zona:
                    qs = qs.filter(zone=zona)

                    # -------- Filtro por FECHA (solo si hay zona) --------
                    fecha_str = self.request.GET.get("fecha")  # formato YYYY-MM-DD
                    if fecha_str:
                        try:
                            fecha = date.fromisoformat(fecha_str)
                            qs = qs.filter(delivery_date=fecha)
                        except ValueError:
                            pass  # fecha malformada → se ignora

                # Orden final
                return qs.order_by("zone", "colonia", "delivery_date")

            def get_context_data(self, **kwargs):
                ctx = super().get_context_data(**kwargs)
                ctx["zonas"] = Order.ZONES
                return ctx



# --------------------------------------------------------------------------- #
#  2. Lista de pedidos asignados (todas las fechas)
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
#  3. Lista de entregas del día
# --------------------------------------------------------------------------- #
class OperatorTodayListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
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
        # apps/orders/views_operator.py
class OperatorAcceptOrderView(LoginRequiredMixin, OperatorRequiredMixin, View):
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

                    # --- NUEVO: vehículo opcional ----------------------------------
                    vehicle = (
                        Vehicle.objects
                        .filter(assigned_operator=request.user, status="active")
                        .first()
                    )
                    # Si no hay pipa, seguimos sin bloquear el flujo
                    if vehicle:
                        order.vehicle = vehicle       # se guarda solo si existe
                    # ----------------------------------------------------------------

                    order.operator   = request.user
                    order.status     = "assigned"
                    order.assigned_at = timezone.now()
                    order.save()

                    Thread.objects.get_or_create(order=order)

                messages.success(request, f"Pedido {order.order_number} asignado correctamente.")
                return redirect(self.success_url)













# --------------------------------------------------------------------------- #
#  5. Rechazar (devolver a la cola)
# --------------------------------------------------------------------------- #
class OperatorRejectOrderView(LoginRequiredMixin, OperatorRequiredMixin, View):
    """Devuelve un pedido asignado a la cola de pendientes."""
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
    """Marca un pedido asignado como entregado."""
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





# apps/orders/views_operator.py
from datetime import date
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Order
from .mixins import OperatorRequiredMixin   # si lo usas




from datetime import date
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Order
from .mixins import OperatorRequiredMixin


class OperatorPendingListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    template_name = "operator/orders_pending.html"
    context_object_name = "orders"

    def get_queryset(self):
        qs = (
            Order.objects
            .filter(status="pending", operator__isnull=True)
            .select_related("client")
        )

        # --- Filtro por ZONA (opcional) ---
        zona = self.request.GET.get("zona")
        if zona:
            qs = qs.filter(zone=zona)

        # --- Filtro por FECHA (opcional, formato YYYY-MM-DD) ---
        fecha_str = self.request.GET.get("fecha")
        if fecha_str:
            try:
                fecha = date.fromisoformat(fecha_str)
                qs = qs.filter(delivery_date=fecha)
            except ValueError:
                pass  # fecha malformada → se ignora

        # Orden final
        return qs.order_by("zone", "colonia", "delivery_date")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["zonas"] = Order.ZONES
        return ctx



# apps/orders/views_operator.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Order           # ajusta el import si tu modelo vive en otra ruta

# apps/orders/views_operator.py
class OperatorHistoryListView(LoginRequiredMixin, ListView):
    template_name = "operator/orders_history.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        return (
            Order.objects
                 .filter(status="delivered", operator=self.request.user)
                 .select_related("client")             # ← antes era customer
                 .order_by("-actual_delivery_date")    # ← campo correcto
        )








# orders/views_operator.py  ← dentro de la MISMA app
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order

class OperatorOrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"  # usa tu ruta real
