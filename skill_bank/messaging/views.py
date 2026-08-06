from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import SkillExchange, Message


def get_demo_user(request):
    """Helper to get current logged in user or default demo user."""
    if request.user.is_authenticated:
        return request.user
    user = User.objects.filter(username='dnyani').first() or User.objects.first()
    return user


def messaging_view(request, exchange_id=None):
    current_user = get_demo_user(request)
    
    # Filter by status if tab selected
    status_filter = request.GET.get('status', 'all').upper()
    
    exchanges_qs = SkillExchange.objects.all()
    if status_filter in ['ACCEPTED', 'REQUESTED', 'COMPLETED', 'IN_PROGRESS']:
        exchanges_qs = exchanges_qs.filter(status=status_filter)
        
    exchanges = list(exchanges_qs)

    for ex in exchanges:
        if current_user and ex.requester == current_user:
            ex.partner = ex.provider
        else:
            ex.partner = ex.provider if current_user == ex.requester else ex.requester

    active_exchange = None
    if exchange_id:
        active_exchange = get_object_or_404(SkillExchange, id=exchange_id)
    elif exchanges:
        active_exchange = exchanges[0]

    # Handle posting a new message directly from the chat screen
    if request.method == 'POST' and active_exchange:
        content = request.POST.get('content', '').strip()
        if content:
            sender = current_user if current_user else active_exchange.requester
            msg = Message.objects.create(
                exchange=active_exchange,
                sender=sender,
                content=content
            )
            # Update exchange timestamp
            active_exchange.save()
            messages.success(request, "Message sent successfully!")
            return redirect('messaging_detail', exchange_id=active_exchange.id)

    chat_messages = []
    partner = None
    if active_exchange:
        chat_messages = active_exchange.messages.select_related('sender').all()
        if current_user and active_exchange.requester == current_user:
            partner = active_exchange.provider
        else:
            partner = active_exchange.provider if current_user == active_exchange.requester else active_exchange.requester

    context = {
        'exchanges': exchanges,
        'active_exchange': active_exchange,
        'chat_messages': chat_messages,
        'current_user': current_user,
        'partner': partner,
        'status_filter': status_filter.lower(),
        'all_users': User.objects.all(),
    }
    return render(request, 'messaging/messaging.html', context)


def send_message_ajax(request, exchange_id):
    if request.method == 'POST':
        active_exchange = get_object_or_404(SkillExchange, id=exchange_id)
        content = request.POST.get('content', '').strip()
        current_user = get_demo_user(request)
        sender = current_user if current_user else active_exchange.requester
        
        if content:
            msg = Message.objects.create(
                exchange=active_exchange,
                sender=sender,
                content=content
            )
            return JsonResponse({
                'status': 'success',
                'id': msg.id,
                'sender': msg.sender.username,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%H:%M')
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid content'}, status=400)
