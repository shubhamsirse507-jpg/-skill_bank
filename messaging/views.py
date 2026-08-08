from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .models import SkillExchange, Conversation, Message
from skill_management.models import Skill


@login_required
def messaging_view(request, exchange_id=None):
    current_user = request.user
    status_filter = request.GET.get('status', 'all').lower()

    # Query exchanges involving current user
    exchanges_qs = SkillExchange.objects.filter(
        Q(requester=current_user) | Q(receiver=current_user)
    ).select_related('requester', 'receiver', 'skill')

    if status_filter in ['pending', 'accepted', 'completed', 'cancelled', 'rejected']:
        exchanges_qs = exchanges_qs.filter(status=status_filter)

    exchanges = list(exchanges_qs)

    for ex in exchanges:
        ex.partner = ex.receiver if ex.requester == current_user else ex.requester

    active_exchange = None
    if exchange_id:
        active_exchange = get_object_or_404(
            SkillExchange.objects.filter(Q(requester=current_user) | Q(receiver=current_user)),
            id=exchange_id
        )
    elif exchanges:
        active_exchange = exchanges[0]

    # Get or create Conversation for active exchange
    conversation = None
    if active_exchange:
        conversation, _ = Conversation.objects.get_or_create(
            request=active_exchange,
            defaults={
                'user_one': active_exchange.requester,
                'user_two': active_exchange.receiver,
            }
        )

    # Handle posting a new message
    if request.method == 'POST' and conversation:
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                conversation=conversation,
                sender=current_user,
                message_text=content
            )
            active_exchange.save()  # update timestamp
            messages.success(request, "Message sent successfully!")
            return redirect('messaging_detail', exchange_id=active_exchange.id)

    chat_messages = []
    partner = None
    if conversation:
        chat_messages = conversation.messages.select_related('sender').all()
        # Mark unread messages as read
        conversation.messages.filter(~Q(sender=current_user), is_read=False).update(is_read=True)
        partner = active_exchange.receiver if active_exchange.requester == current_user else active_exchange.requester

    context = {
        'exchanges': exchanges,
        'active_exchange': active_exchange,
        'conversation': conversation,
        'chat_messages': chat_messages,
        'current_user': current_user,
        'partner': partner,
        'status_filter': status_filter,
    }
    return render(request, 'messaging/messaging.html', context)


@login_required
def send_message_ajax(request, exchange_id):
    """AJAX endpoint to post a message in an exchange conversation."""
    if request.method == 'POST':
        active_exchange = get_object_or_404(
            SkillExchange.objects.filter(Q(requester=request.user) | Q(receiver=request.user)),
            id=exchange_id
        )
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'}, status=400)

        conversation, _ = Conversation.objects.get_or_create(
            request=active_exchange,
            defaults={
                'user_one': active_exchange.requester,
                'user_two': active_exchange.receiver,
            }
        )

        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_text=content
        )
        active_exchange.save()

        return JsonResponse({
            'status': 'success',
            'id': msg.id,
            'sender': msg.sender.username,
            'content': msg.message_text,
            'created_at': msg.created_at.strftime('%H:%M')
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
def create_exchange_request(request):
    """View to initiate a skill exchange request."""
    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        receiver_id = request.POST.get('receiver_id')
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()

        if not skill_id or not receiver_id:
            messages.error(request, 'Invalid skill or receiver selected.')
            return redirect('search_skills')

        skill = get_object_or_404(Skill, pk=skill_id)
        receiver = get_object_or_404(User, pk=receiver_id)

        if receiver == request.user:
            messages.error(request, 'You cannot request an exchange with yourself.')
            return redirect('search_skills')

        exchange = SkillExchange.objects.create(
            requester=request.user,
            receiver=receiver,
            skill=skill,
            title=title or f"Skill Swap: {skill.title}",
            message=message,
            status='pending'
        )

        # Pre-create conversation
        Conversation.objects.create(
            request=exchange,
            user_one=request.user,
            user_two=receiver
        )

        messages.success(request, 'Exchange request sent successfully!')
        return redirect('messaging_detail', exchange_id=exchange.id)

    return redirect('search_skills')
