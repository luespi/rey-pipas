from django.urls import path
from .views_operator import (
    # Listados
    OperatorPendingListView,
    OperatorAssignedListView,
    OperatorTodayListView,
    OperatorHistoryListView,
    # Acciones
    OperatorAcceptOrderView,
    OperatorRejectOrderView,
    OperatorMarkDeliveredView,
    # Detalle
    OperatorOrderDetailView,
)

app_name = "orders_operator"

urlpatterns = [
    # ----- Cola pública -----
    path("pending/",  OperatorPendingListView.as_view(),  name="pending"),
    path("accept/<int:pk>/",  OperatorAcceptOrderView.as_view(),  name="accept"),

    # ----- Pedidos asignados -----
    path("assigned/", OperatorAssignedListView.as_view(), name="assigned"),
    path("today/",    OperatorTodayListView.as_view(),    name="today"),

    # ----- Acciones sobre un pedido -----
    path("<int:pk>/reject/",  OperatorRejectOrderView.as_view(),  name="reject"),
    path("<int:pk>/deliver/", OperatorMarkDeliveredView.as_view(), name="deliver"),

    # ----- Historial -----
    path("history/", OperatorHistoryListView.as_view(), name="history"),

    # ----- Detalle (¡al final!) -----
    path("<int:pk>/", OperatorOrderDetailView.as_view(), name="detail"),
]
