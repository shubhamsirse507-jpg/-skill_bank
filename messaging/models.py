"""
messaging/models.py
Spec tables: exchange_requests, conversations, messages.
Moved from skill_bank/messaging/ and fully restructured to match spec.
"""

from django.db import models
from django.contrib.auth.models import User
from skill_management.models import Skill


class SkillExchange(models.Model):
    """
    Spec table: exchange_requests
    Renamed fields: requester→requester_id, provider→receiver_id.
    requested_skill/offered_skill (free-text) → skill_id FK to canonical Skill.
    Status vocab changed to match spec: pending/accepted/rejected/cancelled/completed.
    Added: message field.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Spec: requester_id
    requester = models.ForeignKey(
        User, related_name='requested_exchanges', on_delete=models.CASCADE
    )
    # Spec: receiver_id
    receiver = models.ForeignKey(
        User, related_name='received_exchanges', on_delete=models.CASCADE
    )
    # Spec: skill_id FK — replaces free-text requested_skill/offered_skill
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name='exchanges',
        help_text='The skill being exchanged'
    )
    # Spec: title (kept — useful for display)
    title = models.CharField(max_length=200, help_text='Topic or goal of the skill exchange')
    # Spec: message — was MISSING
    message = models.TextField(blank=True, default='', help_text='Initial message from requester')
    # Spec: status (new vocabulary)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exchange_requests'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.requester.username} → {self.receiver.username}) [{self.status}]"


class Conversation(models.Model):
    """
    Spec table: conversations
    Sits between exchange_requests and messages.
    """

    request = models.OneToOneField(
        SkillExchange, on_delete=models.CASCADE, related_name='conversation'
    )
    user_one = models.ForeignKey(
        User, related_name='conversations_as_one', on_delete=models.CASCADE
    )
    user_two = models.ForeignKey(
        User, related_name='conversations_as_two', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Conv #{self.id}: {self.user_one.username} ↔ {self.user_two.username}"


class Message(models.Model):
    """
    Spec table: messages
    Repointed to conversation_id (was: exchange directly).
    Renamed content → message_text.
    """

    conversation = models.ForeignKey(
        Conversation, related_name='messages', on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, related_name='sent_messages', on_delete=models.CASCADE
    )
    # Spec: message_text (was: content)
    message_text = models.TextField()

    # Extras kept from old model — fine as additions
    is_read = models.BooleanField(default=False)
    has_attachment = models.BooleanField(default=False)
    attachment_name = models.CharField(max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender.username} in Conv#{self.conversation_id} at {self.created_at.strftime('%H:%M')}"
