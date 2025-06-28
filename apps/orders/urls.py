# apps/orders/urls.py
from django.urls import path
from .views import (
    create_order_view,
    my_orders_view,
    rate_order_view,
    order_detail_view,

)

app_name = "orders"

urlpatterns = [
    path("nueva/", create_order_view, name="create_order"),
    path("mis/",   my_orders_view,   name="my_orders"),
    path("<int:pk>/calificar/", rate_order_view, name="rate_order"),
    path("<int:pk>/detalle/", order_detail_view, name="order_detail"),
]



