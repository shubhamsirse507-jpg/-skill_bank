"""
ratings/models.py
Spec table: reviews
Repointed from exchange FK to booking_id FK per spec requirements.
Renamed reviewer -> reviewer_id, reviewee -> reviewed_user_id.
"""

from django.db import models
from django.contrib.auth.models import User
from bookings.models import Booking


class ReviewRating(models.Model):
    """
    Spec table: reviews
    Follows a completed booking.
    """

    # Spec: booking_id FK — repointed from exchange per spec requirement
    booking = models.ForeignKey(
        Booking, related_name='reviews', on_delete=models.CASCADE
    )
    # Spec: reviewer_id
    reviewer = models.ForeignKey(
        User, related_name='reviews_given', on_delete=models.CASCADE
    )
    # Spec: reviewed_user_id
    reviewed_user = models.ForeignKey(
        User, related_name='reviews_received', on_delete=models.CASCADE
    )

    # Core rating (1-5 stars)
    rating = models.IntegerField(default=5)

    # Sub-ratings (preserved from original model as good additions)
    communication_rating = models.IntegerField(default=5)
    clarity_rating = models.IntegerField(default=5)
    punctuality_rating = models.IntegerField(default=5)

    comment = models.TextField(blank=True, default='')
    tags = models.CharField(
        max_length=255, blank=True,
        help_text="Comma separated highlights (e.g. Great Communicator, Patient)"
    )
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def __str__(self):
        return f"{self.rating}★ Review by {self.reviewer.username} for {self.reviewed_user.username}"

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
