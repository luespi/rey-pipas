from .utils import get_unread_chat_data

def unread_messages_processor(request):
    if request.user.is_authenticated:
        count, order_pk = get_unread_chat_data(request.user)
        return {
            "unread_messages_count": count,
            "unread_message_order_pk": order_pk,
        }
    return {}
