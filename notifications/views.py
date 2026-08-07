from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from authentication.constants import BRAND_LOGO_IMAGE_NAME, AUTH_BACKGROUND_VIDEO_URL

SAMPLE_NOTIFICATIONS = [
    {
        'id': 1,
        'title': 'Skill Swap Request',
        'message': 'Alex Rivera wants to swap React.js & TypeScript for your Python & Django skills.',
        'notification_type': 'skill_request',
        'is_read': False,
        'created_at_str': '10 mins ago',
        'action_url': '/profile/',
        'action_text': 'Accept Swap',
        'sender_name': 'Alex Rivera',
        'sender_avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
    },
    {
        'id': 2,
        'title': 'New Direct Message',
        'message': 'Jordan Smith: "Hey! Let\'s schedule our peer learning session for tomorrow afternoon."',
        'notification_type': 'message',
        'is_read': False,
        'created_at_str': '45 mins ago',
        'action_url': '#',
        'action_text': 'Reply Message',
        'sender_name': 'Jordan Smith',
        'sender_avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jordan',
    },
    {
        'id': 3,
        'title': 'Profile Score Milestone',
        'message': 'Congratulations! Your profile completeness reached 90%. You are now featured on top matches.',
        'notification_type': 'achievement',
        'is_read': True,
        'created_at_str': '2 hours ago',
        'action_url': '/profile/',
        'action_text': 'View Profile',
        'sender_name': 'Skill Bank Bot',
        'sender_avatar': 'https://api.dicebear.com/7.x/bottts/svg?seed=SkillHero',
    },
    {
        'id': 4,
        'title': 'Security Alert',
        'message': 'A new login attempt was detected from Chrome on Windows (192.168.1.45).',
        'notification_type': 'system',
        'is_read': False,
        'created_at_str': '5 hours ago',
        'action_url': '#',
        'action_text': 'Review Security',
        'sender_name': 'System Guard',
        'sender_avatar': 'https://api.dicebear.com/7.x/identicon/svg?seed=SkillBank',
    },
    {
        'id': 5,
        'title': 'Mentorship Request',
        'message': 'Sam Taylor invited you to collaborate on Machine Learning & Data Science roadmap.',
        'notification_type': 'skill_request',
        'is_read': True,
        'created_at_str': '1 day ago',
        'action_url': '/profile/',
        'action_text': 'View Request',
        'sender_name': 'Sam Taylor',
        'sender_avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sam',
    },
]


def notifications_list(request):
    """
    Renders the main Notifications Center UI.
    Uses session-based notifications to enable interactive mark-as-read and deletion.
    """
    if 'notifications_data' not in request.session:
        request.session['notifications_data'] = list(SAMPLE_NOTIFICATIONS)

    notifications_data = request.session['notifications_data']

    unread_count = sum(1 for item in notifications_data if not item.get('is_read'))
    total_count = len(notifications_data)

    return render(request, 'notifications/notifications.html', {
        'notifications': notifications_data,
        'unread_count': unread_count,
        'total_count': total_count,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
    })


def mark_as_read(request, pk):
    """Marks a single notification as read."""
    notifications_data = request.session.get('notifications_data', list(SAMPLE_NOTIFICATIONS))
    for item in notifications_data:
        if item.get('id') == pk:
            item['is_read'] = True
            break
    request.session['notifications_data'] = notifications_data
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'pk': pk})
    return redirect('notifications')


def mark_all_read(request):
    """Marks all notifications as read."""
    notifications_data = request.session.get('notifications_data', list(SAMPLE_NOTIFICATIONS))
    for item in notifications_data:
        item['is_read'] = True
    request.session['notifications_data'] = notifications_data
    request.session.modified = True
    messages.success(request, 'All notifications marked as read.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications')


def delete_notification(request, pk):
    """Deletes a notification item."""
    notifications_data = request.session.get('notifications_data', list(SAMPLE_NOTIFICATIONS))
    notifications_data = [item for item in notifications_data if item.get('id') != pk]
    request.session['notifications_data'] = notifications_data
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'pk': pk})
    return redirect('notifications')


def clear_all_notifications(request):
    """Clears all notifications."""
    request.session['notifications_data'] = []
    request.session.modified = True
    messages.success(request, 'All notifications cleared.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('notifications')
