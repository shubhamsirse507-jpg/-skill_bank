"""
bookings/models.py
New app — spec table: bookings.
Built from scratch to match spec exactly.
"""

from django.db import models
from messaging.models import SkillExchange


class Booking(models.Model):
    """
    Spec table: bookings
    Links a confirmed exchange to a scheduled session.
    """

    MEETING_MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline / In-Person'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Spec: request_id FK
    request = models.ForeignKey(
        SkillExchange,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='The accepted skill exchange this booking belongs to'
    )
    # Spec: scheduled_date
    scheduled_date = models.DateField()
    # Spec: start_time
    start_time = models.TimeField()
    # Spec: end_time
    end_time = models.TimeField()
    # Spec: meeting_mode
    meeting_mode = models.CharField(
        max_length=10, choices=MEETING_MODE_CHOICES, default='online'
    )
    # Spec: meeting_link
    meeting_link = models.URLField(blank=True, default='')
    # Spec: status
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='scheduled')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-scheduled_date', '-start_time']

    def __str__(self):
        return (
            f"Booking #{self.id} — {self.request.title} "
            f"on {self.scheduled_date} [{self.status}]"
        )
