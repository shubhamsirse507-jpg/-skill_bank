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


class Batch(models.Model):
    """Group live classes / scheduled workshops with seat limits."""
    instructor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='batches')
    title = models.CharField(max_length=200)
    category = models.ForeignKey('skill_management.SkillCategory', on_delete=models.CASCADE, related_name='batches')
    description = models.TextField(blank=True, default='')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    max_seats = models.IntegerField(default=15)
    enrolled_count = models.IntegerField(default=0)
    price_credits = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    meeting_link = models.URLField(blank=True, default='https://meet.jit.si/SkillBankBatchRoom')
    status = models.CharField(max_length=20, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"Batch: {self.title} by {self.instructor.username}"


class BatchEnrollment(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='batch_enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('batch', 'student')


from decimal import Decimal

class DoubtCall(models.Model):
    """Instant 15-minute live doubt-solving video calls (₹50 fee: ₹5 Admin / ₹45 Teacher)."""
    learner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='learner_doubts')
    mentor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='mentor_doubts', null=True, blank=True)
    subject = models.CharField(max_length=150)
    question = models.TextField()
    status = models.CharField(max_length=20, default='searching') # searching, active, completed
    meeting_link = models.URLField(blank=True, default='https://meet.jit.si/SkillBankDoubtCall')
    
    # Financial & Session Time Limits
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))
    admin_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))       # 10%
    teacher_earning = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('45.00')) # 90%
    duration_minutes = models.IntegerField(default=15)
    
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    is_teacher_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Doubt #{self.id}: {self.subject} by {self.learner.username} (₹{self.price})"


