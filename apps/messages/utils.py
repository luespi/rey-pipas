from django.utils.timezone import now
from .models import Thread, Message

def get_unread_chat_data(user):
    from apps.orders.models import Order

    if user.user_type not in ['client', 'operator']:
        return 0, None

    orders = Order.objects.filter(**{user.user_type: user}).select_related('thread')
    for order in orders:
        thread = getattr(order, 'thread', None)
        if not thread:
            continue

        last_seen = thread.last_seen_client if user.user_type == 'client' else thread.last_seen_operator
        messages = thread.messages.exclude(sender=user)
        if last_seen:
            messages = messages.filter(created_at__gt=last_seen)

        if messages.exists():
            return messages.count(), order.pk

    return 0, None
