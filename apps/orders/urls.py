# apps/orders/urls.py
from django.urls import path, include
from .views import (
    create_order_view,
    my_orders_view,
    rate_order_view,
    order_detail_view,
    OrderDetailView,
)

app_name = "orders"

urlpatterns = [
    # Rutas de clientes
    path("nueva/", create_order_view, name="create_order"),
    path("mis/",   my_orders_view,   name="my_orders"),
    path("<int:pk>/calificar/", rate_order_view, name="rate_order"),
    path("<int:pk>/detalle/",   order_detail_view, name="order_detail"),

    # Rutas de operador (sub-módulo)
    path(
        "operator/",
        include(
            ("apps.orders.urls_operator", "orders_operator"),
            namespace="orders_operator",
        ),
    ),



    path("driver/orders/<int:pk>/", OrderDetailView.as_view(),
         name="driver_order_detail"),
]




