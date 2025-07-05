# apps/orders/urls_operator.py
from django.urls import path
from .views_operator import (
    OperatorPendingListView,
    OperatorAcceptOrderView,
    OperatorAssignedListView,
    # ↓ importa también las dos vistas nuevas
    OperatorRejectOrderView,
    OperatorMarkDeliveredView,
)

app_name = "orders_operator"



urlpatterns = [
    path("pending/",  OperatorPendingListView.as_view(),  name="pending"),
    path("accept/<int:pk>/",  OperatorAcceptOrderView.as_view(),  name="accept"),
    path("assigned/", OperatorAssignedListView.as_view(), name="assigned"),

    # --- NUEVAS ACCIONES ---
    path("<int:pk>/reject/",  OperatorRejectOrderView.as_view(),  name="reject"),
    path("<int:pk>/deliver/", OperatorMarkDeliveredView.as_view(), name="deliver"),
]
