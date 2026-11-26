"""
notifications/context_processors.py
Injects unread notification and message counts into every template context.
Runs only for authenticated users; silently returns zeros on any error.
"""


def unread_counts(request):
    """
    Returns:
        nav_unread_notifications  – unread Notification objects for current user
        nav_unread_messages       – unread messages across all conversations
    """
    if not request.user.is_authenticated:
        return {
            'nav_unread_notifications': 0,
            'nav_unread_messages': 0,
        }

    notif_count = 0
    msg_count = 0

    try:
        from .models import Notification
        notif_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    except Exception:
        pass

    try:
        from messaging.models import Conversation
        from django.db.models import Q
        conversations = Conversation.objects.filter(
            Q(user_one=request.user) | Q(user_two=request.user)
        ).prefetch_related('messages')
        for conv in conversations:
            msg_count += conv.messages.filter(
                is_read=False
            ).exclude(sender=request.user).count()
    except Exception:
        pass

    return {
        'nav_unread_notifications': notif_count,
        'nav_unread_messages': msg_count,
    }
