# django_project/urls.py
# URLs principales para Rey Pipas  (sin carpeta “config”)

from django.utils import timezone
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.db.models import Avg
from apps.users.views import dashboard_redirect
# ---------------------------------------------------------------------------
# Vistas de nivel proyecto
# ---------------------------------------------------------------------------

def home_view(request):
    """Página de inicio; si el usuario ya inició sesión lo redirige a su dashboard."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "landing/index.html")


@login_required
def dashboard_view(request):
    """Dashboard principal (admin / operador / cliente)."""
    user = request.user
    user_type = getattr(user, "user_type", "client")
    context = {"user": user, "user_type": user_type}

    from apps.orders.models import Order          # se mantiene igual

    # --- Panel ADMIN ------------------------------------------------------
    if user_type == "admin":
        from apps.users.models import User
        from apps.unidades.models import Unidad   # ← nueva importación

        total_orders      = Order.objects.count()
        pending_orders    = Order.objects.filter(status="pending").count()
        total_clients     = User.objects.filter(user_type="client").count()
        total_unidades    = Unidad.objects.count()          # ← sin campo “status”

        context.update(
            total_orders=total_orders,
            pending_orders=pending_orders,
            total_clients=total_clients,
            total_unidades=total_unidades,       # llave que puedes usar en plantillas
            cards=[
                {"title": "Órdenes totales",      "content": total_orders},
                {"title": "Pendientes",           "content": pending_orders},
                {"title": "Clientes",             "content": total_clients},
                {"title": "Unidades registradas", "content": total_unidades},
            ],
        )
        template = "dashboard/admin_dashboard.html"

    # --- Panel OPERADOR ---------------------------------------------------
    elif user_type == "operator":
        assigned_orders  = Order.objects.filter(operator=user).count()
        today_deliveries = Order.objects.filter(
            operator=user,
            delivery_date=timezone.localdate()
        ).count()

        avg = (
            Order.objects
                 .filter(operator=user, rating__isnull=False)
                 .aggregate(prom=Avg("rating__rating"))
        )["prom"] or 0
        avg_rating = round(avg, 2)

        context.update(
            assigned_orders=assigned_orders,
            today_deliveries=today_deliveries,
            avg_rating=avg_rating,
            cards=[
                {"title": "Órdenes asignadas", "content": assigned_orders},
                {"title": "Entregas hoy",      "content": today_deliveries},
                {"title": "Promedio ⭐",        "content": avg_rating},
            ],
        )
        template = "dashboard/operator_dashboard.html"

    # --- Panel CLIENTE ----------------------------------------------------
    else:
        my_orders_count = Order.objects.filter(client=user).count()
        pending_orders  = Order.objects.filter(client=user, status="pending").count()
        last_orders     = Order.objects.filter(client=user).order_by("-created_at")[:3]

        context.update(
            my_orders=my_orders_count,
            pending_orders=pending_orders,
            last_orders=last_orders,
            cards=[
                {"title": "Mis pedidos", "content": my_orders_count},
                {"title": "Pendientes",  "content": pending_orders},
            ],
        )
        template = "dashboard/client_dashboard.html"

    return render(request, template, context)


# ---------------------------------------------------------------------------
# URL patterns
# ---------------------------------------------------------------------------
urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Páginas principales
    path("",           home_view,      name="home"),

    
    path("dashboard/", dashboard_redirect, name="dashboard"),

    # Autenticación
    path("auth/", include("apps.users.urls")),

    # Apps de dominio
    path("orders/", include("apps.orders.urls")),
    path(
        "orders/operator/",
        include(("apps.orders.urls_operator", "orders_operator"), namespace="orders_operator"),
    ),

    # Nueva app de unidades (reemplaza a vehicles)
    
    path("dashboard/unidades/", include("apps.unidades.urls", namespace="unidades")),


    path("payments/", include("apps.payments.urls")),   # única inclusión de pagos

    # API (futuras integraciones)
    path("api/v1/", include("apps.core.api_urls")),
    # path("api-auth/", include("rest_framework.urls")),  # Descomenta si usas DRF
    path("messages/", include(("apps.messages.urls", "messages"), namespace="messages")),
]

# ---------------------------------------------------------------------------
# BLOQUE DEMO — solo para previsualizar el Operator Dashboard
# ---------------------------------------------------------------------------
urlpatterns += [
    path(
        "demo/operator/",
        TemplateView.as_view(
            template_name="dashboard/operator_dashboard.html",
            extra_context={
                "cards": [
                    {"title": "Órdenes activas",   "content": 12},
                    {"title": "Entregas hoy",      "content": 5},
                    {"title": "Pipas disponibles", "content": 3},
                ]
            },
        ),
        name="demo-operator",
    ),
]

# Archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,  document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,   document_root=settings.MEDIA_ROOT)

# Personalización del sitio admin
admin.site.site_header  = "Rey Pipas - Administración"
admin.site.site_title   = "Rey Pipas Admin"
admin.site.index_title  = "Panel de Administración"
