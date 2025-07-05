from django.urls import path
from .views import OrderChatView   # la vista la harás después

app_name = "messages"

urlpatterns = [
    path("order/<int:pk>/", OrderChatView.as_view(), name="order_chat"),
]
