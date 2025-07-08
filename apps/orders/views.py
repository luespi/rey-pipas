# apps/orders/views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import OrderRequestForm
from .models import Order
from apps.messages.models import Message



@login_required
def create_order_view(request):
    if not request.user.is_client:
        messages.error(request, "Solo los clientes pueden crear pedidos.")
        return redirect("dashboard")

    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user        # ← asigna el cliente
            order.save()
            messages.success(request, "✅ Pedido creado correctamente.")
            return redirect("orders:my_orders")
        else:
            messages.error(request, "Corrige los errores señalados.")
    else:
        form = OrderRequestForm()

    return render(request, "orders/create_order.html", {"form": form})


# apps/orders/views.py  (añade abajo)
@login_required
def my_orders_view(request):
    orders = Order.objects.filter(client=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})




# apps/orders/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, OrderRating
from .forms  import OrderRatingForm

@login_required
def rate_order_view(request, pk):
    order = get_object_or_404(
        Order,
        pk=pk,
        client=request.user,      # asegúrate de tener el FK client en Order
        status="delivered",
    )

    # Evita calificar dos veces
    if hasattr(order, "rating"):
        return redirect("orders:my_orders")

    if request.method == "POST":
        form = OrderRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.order = order
            rating.save()
            return redirect("orders:my_orders")
    else:
        form = OrderRatingForm()

    return render(
        request,
        "orders/rate_order.html",
        {"form": form, "order": order},
    )




from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required



from apps.messages.models import Message



from apps.messages.models import Message

@login_required
def order_detail_view(request, pk):
        order = get_object_or_404(Order, pk=pk, client=request.user)

        # mensajes ligados al hilo del pedido
        messages_qs = (
            Message.objects
            .filter(thread__order=order)        #  👈  OJO: thread__order
            .select_related("sender")
            .order_by("created_at")
        )

        return render(
            request,
            "orders/order_detail.html",
            {
                "order": order,
                "messages": messages_qs,        #  👈  ya no dará error
            },
        )









# apps/orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy

# antes
# from .models import Payment
from apps.payments.models import Payment

from .forms import PaymentForm


class PaymentCreate(LoginRequiredMixin, CreateView):
    model         = Payment
    form_class    = PaymentForm
    template_name = 'orders/payment_form.html'

    def form_valid(self, form):
        form.instance.order_id = self.kwargs['order_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('payments:list')


class PaymentList(LoginRequiredMixin, ListView):
    model         = Payment
    template_name = 'orders/payment_list.html'
    paginate_by   = 20

    def get_queryset(self):
        return (
            Payment.objects
            .filter(order__client=self.request.user)
            .select_related('order')
        )
