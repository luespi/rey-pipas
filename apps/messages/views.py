from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

class OrderChatView(TemplateView):
    """Stub temporal: sólo muestra un placeholder."""
    template_name = "messages/chat_placeholder.html"
