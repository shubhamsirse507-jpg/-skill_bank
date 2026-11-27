from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q, Case, When, IntegerField
from bookings.models import Booking
from .models import ReviewRating


def _clamp_rating(value, default=5):
    """Parse and clamp a 1-5 integer rating value."""
    parsed = int(value if value not in (None, '') else default)
    return max(1, min(5, parsed))


def _booking_partner(booking, user):
    """Return the other participant in a booking, or None if user is not a participant."""
    requester = booking.request.requester
    receiver = booking.request.receiver
    if user == requester:
        return receiver
    if user == receiver:
        return requester
    return None


@login_required
def rating_view(request):
    current_user = request.user
    tab = request.GET.get('tab', 'all')
    if tab not in ('all', 'received', 'given'):
        tab = 'all'

    selected_booking_id = request.GET.get('booking_id', '')

    # Handle submitting new rating form
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        if not booking_id:
            messages.error(request, 'Please select a session to review.')
            return redirect('ratings:rating_dashboard')

        booking = get_object_or_404(
            Booking.objects.select_related('request', 'request__requester', 'request__receiver'),
            id=booking_id
        )

        reviewed_user = _booking_partner(booking, current_user)
        if reviewed_user is None:
            messages.error(request, 'You are not authorized to review this booking.')
            return redirect('ratings:rating_dashboard')

        if booking.status == 'cancelled':
            messages.error(request, 'Cancelled bookings cannot be reviewed.')
            return redirect('ratings:rating_dashboard')

        if ReviewRating.objects.filter(booking=booking, reviewer=current_user).exists():
            messages.warning(request, 'You have already submitted a review for this session.')
            return redirect('ratings:rating_dashboard')

        try:
            rating = _clamp_rating(request.POST.get('rating', 5))
            comm_rating = _clamp_rating(request.POST.get('communication_rating', 5))
            clarity_rating = _clamp_rating(request.POST.get('clarity_rating', 5))
            punc_rating = _clamp_rating(request.POST.get('punctuality_rating', 5))
        except (TypeError, ValueError):
            messages.error(request, 'Invalid rating value.')
            return redirect('ratings:rating_dashboard')

        comment = request.POST.get('comment', '').strip()
        if not comment:
            messages.error(request, 'Please enter feedback comments before submitting.')
            return redirect('ratings:rating_dashboard')

        tags = request.POST.get('tags', '').strip()
        would_recommend = request.POST.get('would_recommend') == 'on'

        ReviewRating.objects.create(
            booking=booking,
            reviewer=current_user,
            reviewed_user=reviewed_user,
            rating=rating,
            communication_rating=comm_rating,
            clarity_rating=clarity_rating,
            punctuality_rating=punc_rating,
            comment=comment,
            tags=tags,
            would_recommend=would_recommend,
        )

        if booking.status != 'completed':
            booking.status = 'completed'
            booking.save(update_fields=['status'])

        messages.success(request, 'Thank you! Your review has been published.')
        return redirect('ratings:rating_dashboard')

    try:
        all_reviews = ReviewRating.objects.select_related(
            'reviewer', 'reviewed_user', 'booking', 'booking__request', 'booking__request__skill'
        ).all()
        total_reviews = all_reviews.count()
        avg_rating = round(all_reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0, 1)
        avg_comm = round(all_reviews.aggregate(Avg('communication_rating'))['communication_rating__avg'] or 0.0, 1)
        avg_clarity = round(all_reviews.aggregate(Avg('clarity_rating'))['clarity_rating__avg'] or 0.0, 1)
        avg_punc = round(all_reviews.aggregate(Avg('punctuality_rating'))['punctuality_rating__avg'] or 0.0, 1)
        rec_count = all_reviews.filter(would_recommend=True).count()
        recommend_pct = int((rec_count / total_reviews * 100)) if total_reviews > 0 else 0

        star_counts = {s: all_reviews.filter(rating=s).count() for s in range(1, 6)}
        star_percents = {
            s: int((count / total_reviews * 100)) if total_reviews > 0 else 0
            for s, count in star_counts.items()
        }
        star_breakdown = [
            {'star': s, 'count': star_counts[s], 'percent': star_percents[s]}
            for s in range(5, 0, -1)
        ]

        if tab == 'received':
            reviews = all_reviews.filter(reviewed_user=current_user)
        elif tab == 'given':
            reviews = all_reviews.filter(reviewer=current_user)
        else:
            reviews = all_reviews

        # Allow reviewing completed or scheduled sessions not yet reviewed by current_user
        unreviewed_bookings = (
            Booking.objects.filter(
                Q(request__requester=current_user) | Q(request__receiver=current_user),
                status__in=['completed', 'scheduled'],
            )
            .exclude(reviews__reviewer=current_user)
            .select_related('request', 'request__requester', 'request__receiver', 'request__skill')
            .annotate(
                status_order=Case(
                    When(status='completed', then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            )
            .order_by('status_order', '-scheduled_date')
        )
    except Exception:
        reviews = []
        total_reviews = 0
        avg_rating = 0.0
        avg_comm = 0.0
        avg_clarity = 0.0
        avg_punc = 0.0
        recommend_pct = 0
        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        star_percents = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        star_breakdown = [{'star': s, 'count': 0, 'percent': 0} for s in range(5, 0, -1)]
        unreviewed_bookings = []

    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'avg_comm': avg_comm,
        'avg_clarity': avg_clarity,
        'avg_punc': avg_punc,
        'recommend_pct': recommend_pct,
        'star_counts': star_counts,
        'star_percents': star_percents,
        'star_breakdown': star_breakdown,
        'unreviewed_bookings': unreviewed_bookings,
        'selected_booking_id': selected_booking_id,
        'tab': tab,
        'current_user': current_user,
    }
    return render(request, 'ratings/rating.html', context)


# ---------------------------------------------------------------------------
# DRF API Views
# ---------------------------------------------------------------------------
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import ReviewRatingSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReviewRating.objects.filter(
            Q(reviewed_user=self.request.user) | Q(reviewer=self.request.user)
        ).select_related('reviewer', 'reviewed_user', 'booking')

    def perform_create(self, serializer):
        booking = serializer.validated_data['booking']
        reviewer = self.request.user
        reviewed_user = _booking_partner(booking, reviewer)
        if reviewed_user is None:
            raise PermissionDenied('You are not a participant in this booking.')
        if booking.status == 'cancelled':
            raise ValidationError({'booking': 'Cancelled bookings cannot be reviewed.'})
        if ReviewRating.objects.filter(booking=booking, reviewer=reviewer).exists():
            raise ValidationError({'booking': 'You have already reviewed this booking.'})
        serializer.save(reviewer=reviewer, reviewed_user=reviewed_user)
        if booking.status != 'completed':
            booking.status = 'completed'
            booking.save(update_fields=['status'])


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = ReviewRating.objects.all()
    serializer_class = ReviewRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

