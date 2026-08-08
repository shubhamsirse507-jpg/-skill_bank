from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Notification
from authentication.constants import BRAND_LOGO_IMAGE_NAME, AUTH_BACKGROUND_VIDEO_URL


@login_required
def notifications_list(request):
    """Renders main Notifications Center UI using database Notification model."""
    notifications_qs = Notification.objects.filter(user=request.user)

    unread_count = notifications_qs.filter(is_read=False).count()
    total_count = notifications_qs.count()

    return render(request, 'notifications/notifications.html', {
        'notifications': notifications_qs,
        'unread_count': unread_count,
        'total_count': total_count,
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
