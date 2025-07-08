# apps/messages/urls.py
from django.urls import path
from .views import OrderChatView, create_message

app_name = "messages"
urlpatterns = [
    path("order/<int:pk>/", OrderChatView.as_view(), name="order_chat"),
    path("order/<int:order_pk>/create/", create_message, name="create"),
]
