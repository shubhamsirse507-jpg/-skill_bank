from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Booking
from messaging.models import SkillExchange


@login_required
def booking_list(request):
    """Lists bookings for current user (as requester or receiver)."""
    bookings = []
    error_msg = None

    try:
        user_exchanges = list(SkillExchange.objects.filter(
            Q(requester=request.user) | Q(receiver=request.user)
        ))
        # Use list() to force QuerySet evaluation HERE (inside try/except),
        # not lazily in the template where we can't catch OperationalError.
        bookings = list(
            Booking.objects.filter(request__in=user_exchanges).select_related(
                'request', 'request__requester', 'request__receiver', 'request__skill'
            )
        )
    except Exception as e:
        error_msg = str(e)
        bookings = []

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
        'error_msg': error_msg,
    })


@login_required
def create_booking(request, exchange_id):
    """Schedules a new booking for an accepted exchange."""
    exchange = get_object_or_404(
        SkillExchange.objects.filter(Q(requester=request.user) | Q(receiver=request.user)),
        id=exchange_id
    )

    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meeting_mode = request.POST.get('meeting_mode', 'online')
        meeting_link = request.POST.get('meeting_link', '').strip()

        if not scheduled_date or not start_time or not end_time:
            messages.error(request, 'Please provide date, start time, and end time.')
            return redirect('create_booking', exchange_id=exchange_id)

        booking = Booking.objects.create(
            request=exchange,
            scheduled_date=scheduled_date,
            start_time=start_time,
            end_time=end_time,
            meeting_mode=meeting_mode,
            meeting_link=meeting_link,
            status='scheduled'
        )

        messages.success(request, 'Session booked successfully!')
        return redirect('booking_list')

    return render(request, 'bookings/create_booking.html', {
        'exchange': exchange,
    })
