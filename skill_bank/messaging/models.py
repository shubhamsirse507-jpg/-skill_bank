from django.db import models
from django.contrib.auth.models import User


class SkillExchange(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('ACCEPTED', 'Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    requester = models.ForeignKey(User, related_name='requested_exchanges', on_delete=models.CASCADE)
    provider = models.ForeignKey(User, related_name='provided_exchanges', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="Topic or goal of the skill exchange")
    requested_skill = models.CharField(max_length=100)
    offered_skill = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACCEPTED')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.requester.username} <-> {self.provider.username})"

    class Meta:
        ordering = ['-updated_at']


class Message(models.Model):
    exchange = models.ForeignKey(SkillExchange, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    has_attachment = models.BooleanField(default=False)
    attachment_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg from {self.sender.username} in #{self.exchange.id} at {self.created_at.strftime('%H:%M')}"

    class Meta:
        ordering = ['created_at']
