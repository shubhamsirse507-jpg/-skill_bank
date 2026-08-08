from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Notification
from authentication.constants import BRAND_LOGO_IMAGE_NAME, AUTH_BACKGROUND_VIDEO_URL


@login_required
def notifications_list(request):
    """Renders main Notifications Center UI with Notifications, Messages, and Ratings tabs."""
    notifications_qs = Notification.objects.filter(user=request.user)
    unread_count = notifications_qs.filter(is_read=False).count()
    total_count = notifications_qs.count()

    # ── Messages: pull recent conversations where user participates ──────────
    recent_messages = []
    unread_messages_count = 0
    try:
        from messaging.models import Conversation, Message
        from django.db.models import Q, Max, Subquery, OuterRef
        conversations = Conversation.objects.filter(
            Q(user_one=request.user) | Q(user_two=request.user)
        ).prefetch_related('messages', 'messages__sender').select_related('user_one', 'user_two', 'request')

        for conv in conversations:
            latest = conv.messages.last()
            if latest:
                other_user = conv.user_two if conv.user_one == request.user else conv.user_one
                unread_in_conv = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
                unread_messages_count += unread_in_conv
                recent_messages.append({
                    'conversation': conv,
                    'latest_message': latest,
                    'other_user': other_user,
                    'unread_count': unread_in_conv,
                    'exchange_title': conv.request.title if conv.request else 'Skill Exchange',
                })
        recent_messages.sort(key=lambda x: x['latest_message'].created_at, reverse=True)
    except Exception:
        pass

    # ── Ratings: pull reviews received by this user ──────────────────────────
    received_ratings = []
    try:
        from ratings.models import ReviewRating
        received_ratings = list(
            ReviewRating.objects.filter(reviewed_user=request.user)
            .select_related('reviewer', 'booking')
            .order_by('-created_at')[:20]
        )
    except Exception:
        pass

    return render(request, 'notifications/notifications.html', {
        'notifications': notifications_qs,
        'unread_count': unread_count,
        'total_count': total_count,
        'recent_messages': recent_messages,
        'unread_messages_count': unread_messages_count,
        'received_ratings': received_ratings,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
    })


@login_required
def mark_as_read(request, pk):
    """Marks a single notification as read."""
    Notification.objects.filter(user=request.user, pk=pk).update(is_read=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'pk': pk})
    return redirect('notifications')


@login_required
def mark_all_read(request):
    """Marks all notifications for current user as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications')


@login_required
def delete_notification(request, pk):
    """Deletes a notification item."""
    Notification.objects.filter(user=request.user, pk=pk).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'pk': pk})
    return redirect('notifications')


@login_required
def clear_all_notifications(request):
    """Clears all notifications for user."""
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, 'All notifications cleared.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications')
