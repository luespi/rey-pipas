# apps/orders/urls_operator.py
from django.urls import path
from .views_operator import (
    OperatorPendingListView,
    OperatorAcceptOrderView,
    OperatorAssignedListView,
    OperatorTodayListView,
    OperatorRejectOrderView,
    OperatorMarkDeliveredView,
    OperatorHistoryListView,          # ← incluido en la misma lista
)

app_name = "orders_operator"

urlpatterns = [
    # Cola pública de pedidos pendientes
    path("pending/",  OperatorPendingListView.as_view(),  name="pending"),
    path("accept/<int:pk>/",  OperatorAcceptOrderView.as_view(),  name="accept"),

    # Pedidos ya asignados al operador
    path("assigned/", OperatorAssignedListView.as_view(), name="assigned"),
    path("today/",    OperatorTodayListView.as_view(),    name="today"),

    # Acciones sobre un pedido asignado
    path("<int:pk>/reject/",  OperatorRejectOrderView.as_view(),  name="reject"),
    path("<int:pk>/deliver/", OperatorMarkDeliveredView.as_view(), name="deliver"),

    # Historial de entregas
    path("history/", OperatorHistoryListView.as_view(), name="history"),   # ← nombre unificado
]

