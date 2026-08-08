from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from bookings.models import Booking
from .models import ReviewRating


@login_required
def rating_view(request):
    current_user = request.user
    reviews = ReviewRating.objects.select_related('reviewer', 'reviewed_user', 'booking').all()

    # Calculate Summary Stats
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
    avg_rating = round(avg_rating, 1)

    avg_comm = reviews.aggregate(Avg('communication_rating'))['communication_rating__avg'] or 0.0
    avg_comm = round(avg_comm, 1)

    avg_clarity = reviews.aggregate(Avg('clarity_rating'))['clarity_rating__avg'] or 0.0
    avg_clarity = round(avg_clarity, 1)

    avg_punc = reviews.aggregate(Avg('punctuality_rating'))['punctuality_rating__avg'] or 0.0
    avg_punc = round(avg_punc, 1)

    rec_count = reviews.filter(would_recommend=True).count()
    recommend_pct = int((rec_count / total_reviews * 100)) if total_reviews > 0 else 100

    star_counts = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }
    star_percents = {}
    for star, count in star_counts.items():
        star_percents[star] = int((count / total_reviews * 100)) if total_reviews > 0 else 0

    # User's bookings ready to review
    unreviewed_bookings = Booking.objects.filter(
        Q(request__requester=current_user) | Q(request__receiver=current_user),
        status='completed',
        reviews__isnull=True
    ).select_related('request', 'request__requester', 'request__receiver')

    # Handle submitting new rating form
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        if not booking_id:
            messages.error(request, 'Booking ID is required.')
            return redirect('rating_dashboard')

        booking = get_object_or_404(Booking, id=booking_id)

        # Confirm user is participant
        requester = booking.request.requester
        receiver = booking.request.receiver
        if current_user not in (requester, receiver):
            messages.error(request, 'You are not authorized to review this booking.')
            return redirect('rating_dashboard')

        reviewer = current_user
        reviewed_user = receiver if reviewer == requester else requester

        try:
            rating = max(1, min(5, int(request.POST.get('rating', 5))))
            comm_rating = max(1, min(5, int(request.POST.get('communication_rating', 5))))
            clarity_rating = max(1, min(5, int(request.POST.get('clarity_rating', 5))))
            punc_rating = max(1, min(5, int(request.POST.get('punctuality_rating', 5))))
        except ValueError:
            messages.error(request, 'Invalid rating value.')
            return redirect('rating_dashboard')

        comment = request.POST.get('comment', '').strip()
        tags = request.POST.get('tags', '')
        would_recommend = request.POST.get('would_recommend') == 'on'

        ReviewRating.objects.create(
            booking=booking,
            reviewer=reviewer,
            reviewed_user=reviewed_user,
            rating=rating,
            communication_rating=comm_rating,
            clarity_rating=clarity_rating,
            punctuality_rating=punc_rating,
            comment=comment,
            tags=tags,
            would_recommend=would_recommend
        )

        booking.status = 'completed'
        booking.save()

        messages.success(request, "Thank you! Your review has been published.")
        return redirect('rating_dashboard')

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
        'unreviewed_bookings': unreviewed_bookings,
        'current_user': current_user,
    }
    return render(request, 'ratings/rating.html', context)


# ---------------------------------------------------------------------------
# DRF API Views
# ---------------------------------------------------------------------------
from rest_framework import generics, permissions
from .serializers import ReviewRatingSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReviewRating.objects.filter(
            reviewed_user=self.request.user
        ).select_related('reviewer', 'reviewed_user', 'booking')

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = ReviewRating.objects.all()
    serializer_class = ReviewRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

