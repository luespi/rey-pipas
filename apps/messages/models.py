from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

class Thread(models.Model):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="threads"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thread #{self.pk} – Order {self.order_id or 'general'}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
       return f"{self.sender} · {self.text[:30]}…"
