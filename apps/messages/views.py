# apps/messages/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.orders.models import Order
from apps.messages.models import Thread, Message











@method_decorator(login_required, name="dispatch")
class OrderChatView(TemplateView):
    """
    • Petición normal       → página completa (chat_page.html)
    • Petición HTMX (ajax)  → sólo la lista (_list.html)
    """
    def get_template_names(self): # type: ignore[override]
        if self.request.headers.get("HX-Request"):
            return ["messages/_list.html"]
        return ["messages/chat_page.html"]

    # ---------------------------------------------------------------------- #
    #                               dispatch                                 #
    # ---------------------------------------------------------------------- #
    def dispatch(self, request, *args, **kwargs):
        # 1. Traer la orden
        self.order = get_object_or_404(Order, pk=kwargs["pk"])

        # 2. Autorizar a cliente u operador únicamente
        if request.user not in (self.order.client, self.order.operator):
            return HttpResponseForbidden("No autorizado")

        # 3. Garantizar que exista un Thread para la orden
        Thread.objects.get_or_create(order=self.order)

        return super().dispatch(request, *args, **kwargs)

    # ---------------------------------------------------------------------- #
    #                            get_context_data                            #
    # ---------------------------------------------------------------------- #
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        thread = self.order.thread                     # One‑to‑One asegurado
        ctx["messages"] = (
            Message.objects
            .filter(thread=thread)
            .select_related("sender")
            .order_by("created_at")
        )
        ctx["order"] = self.order                      # útil si la plantilla lo requiere
        return ctx


# --------------------------------------------------------------------------- #
#                              crear mensaje                                  #
# --------------------------------------------------------------------------- #
@require_POST
@login_required
def create_message(request, order_pk):
    """
    Guarda un mensaje y devuelve 204 (sin contenido).
    El frontend HTMX refresca #chat‑box en la siguiente llamada.
    """
    order = get_object_or_404(Order, pk=order_pk)

    # Seguridad: sólo cliente u operador del pedido
    if request.user not in (order.client, order.operator):
        return HttpResponseForbidden("No autorizado")

    text = request.POST.get("body", "").strip()
    if not text:                                     # nada que guardar
        return HttpResponse(status=204)

    thread, _ = Thread.objects.get_or_create(order=order)
    Message.objects.create(thread=thread,
                           sender=request.user,
                           text=text)
    return HttpResponse(status=204)
