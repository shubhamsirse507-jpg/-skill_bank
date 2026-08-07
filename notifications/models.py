from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPE_CHOICES = (
        ('skill_request', 'Skill Swap Request'),
        ('system', 'System Notification'),
        ('message', 'Direct Message'),
        ('achievement', 'Skill Achievement'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.CharField(max_length=255, blank=True, default='')
    action_text = models.CharField(max_length=100, blank=True, default='')
    sender_name = models.CharField(max_length=100, blank=True, default='')
    sender_avatar = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username if self.user else 'Guest'}"
