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


from decimal import Decimal
import uuid


@login_required
def create_exchange_request(request):
    """View to initiate a skill exchange request with user-defined price (max ₹100)."""
    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        receiver_id = request.POST.get('receiver_id')
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        price_val = request.POST.get('price', '0.00').strip()

        # Validate and cap price between ₹0 and ₹100
        try:
            price = Decimal(price_val)
            if price < Decimal('0.00'):
                price = Decimal('0.00')
            elif price > Decimal('100.00'):
                price = Decimal('100.00')
        except Exception:
            price = Decimal('0.00')

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
            price=price,
            status='pending'
        )

        # Pre-create conversation
        Conversation.objects.create(
            request=exchange,
            user_one=request.user,
            user_two=receiver
        )

        # Notify receiver
        try:
            from notifications.models import Notification
            price_text = f" (Price: ₹{price:.2f})" if price > 0 else " (Free Swap)"
            Notification.objects.create(
                user=receiver,
                title="New Skill Exchange Request",
                message=f"{request.user.first_name or request.user.username} requested a swap for {skill.title}{price_text}.",
                type="skill_request",
                action_url=f"/messaging/messages/{exchange.id}/",
                action_text="View Request"
            )
        except Exception:
            pass

        messages.success(request, f'Exchange request sent successfully! (Price: ₹{price:.2f})')
        return redirect('messaging_detail', exchange_id=exchange.id)

    return redirect('search_skills')


@login_required
def update_exchange_status(request, exchange_id, action):
    """Accept, reject, complete, or cancel a skill exchange request with wallet payment on accept."""
    exchange = get_object_or_404(
        SkillExchange.objects.filter(Q(requester=request.user) | Q(receiver=request.user)),
        id=exchange_id
    )

    action = action.lower()
    if action == 'accept':
        # Process Payment if price > 0
        if exchange.price > Decimal('0.00'):
            from payments.models import Wallet, WalletTransaction, PaymentReceipt

            requester_wallet, _ = Wallet.objects.get_or_create(user=exchange.requester)
            if requester_wallet.balance < exchange.price:
                messages.error(
                    request,
                    f'Cannot accept: Requester @{exchange.requester.username} has insufficient wallet balance (₹{exchange.price:.2f} required).'
                )
                return redirect('messaging_detail', exchange_id=exchange.id)

            # Deduct full price from requester
            requester_wallet.balance = Decimal(str(requester_wallet.balance)) - exchange.price
            requester_wallet.save()

            WalletTransaction.objects.create(
                wallet=requester_wallet,
                amount=exchange.price,
                transaction_type='debit',
                description=f"Skill Swap Payment: '{exchange.title}'"
            )

            # Splits: 10% Admin, 90% Provider
            admin_fee = (exchange.price * Decimal('0.10')).quantize(Decimal('0.01'))
            provider_earning = exchange.price - admin_fee

            admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
            if admin_user:
                admin_wallet, _ = Wallet.objects.get_or_create(user=admin_user)
                admin_wallet.balance = Decimal(str(admin_wallet.balance)) + admin_fee
                admin_wallet.earned_total = Decimal(str(admin_wallet.earned_total)) + admin_fee
                admin_wallet.save()

                WalletTransaction.objects.create(
                    wallet=admin_wallet,
                    amount=admin_fee,
                    transaction_type='credit',
                    description=f"Admin 10% Fee from Skill Swap #{exchange.id}"
                )

            provider_wallet, _ = Wallet.objects.get_or_create(user=exchange.receiver)
            provider_wallet.balance = Decimal(str(provider_wallet.balance)) + provider_earning
            provider_wallet.earned_total = Decimal(str(provider_wallet.earned_total)) + provider_earning
            provider_wallet.save()

            WalletTransaction.objects.create(
                wallet=provider_wallet,
                amount=provider_earning,
                transaction_type='credit',
                description=f"Earned 90% (₹{provider_earning:.2f}) from Skill Swap: '{exchange.title}'"
            )

            # Create Payment Receipt
            tx_id = f"TXN-SWP-{uuid.uuid4().hex[:8].upper()}"
            receipt = PaymentReceipt.objects.create(
                student=exchange.requester,
                teacher=exchange.receiver,
                item_title=f"Skill Swap: {exchange.title}",
                category_name='Skill Exchange',
                amount=exchange.price,
                payment_method='SkillBank Wallet',
                transaction_id=tx_id,
                status='PAID'
            )
            rec_num = str(receipt.receipt_number)[:8]

            messages.success(
                request,
                f'Skill exchange accepted! ₹{exchange.price:.2f} payment processed (₹{provider_earning:.2f} credited to provider wallet, receipt #{rec_num}).'
            )
        else:
            messages.success(request, 'Skill exchange accepted!')

        exchange.status = 'accepted'

        # Auto-create initial scheduled booking if none exists
        try:
            from bookings.models import Booking
            from datetime import date, time
            if not Booking.objects.filter(request=exchange).exists():
                Booking.objects.create(
                    request=exchange,
                    scheduled_date=date.today(),
                    start_time=time(14, 0),
                    end_time=time(15, 0),
                    meeting_mode='online',
                    meeting_link='https://meet.google.com/demo-skill-bank',
                    status='scheduled'
                )
        except Exception:
            pass

    elif action == 'reject':
        exchange.status = 'rejected'
        messages.info(request, 'Skill exchange rejected.')
    elif action == 'complete':
        exchange.status = 'completed'
        messages.success(request, 'Skill exchange marked as completed!')
    elif action == 'cancel':
        exchange.status = 'cancelled'
        messages.warning(request, 'Skill exchange cancelled.')

    exchange.save()
    return redirect('messaging_detail', exchange_id=exchange.id)


