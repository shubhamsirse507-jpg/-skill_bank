from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class PlatformCallSettings(models.Model):
    """
    Singleton platform-wide configuration for built-in WebRTC calling.
    Controlled by platform admins via Django Admin or the Admin Panel UI.
    """

    calling_enabled = models.BooleanField(
        default=True,
        help_text='Global master switch to enable or disable calling across the platform.',
    )
    max_participants = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(2), MaxValueValidator(10)],
        help_text='Maximum participants allowed in any call room (server-capped at 10).',
    )
    max_call_duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(480)],
        help_text='Maximum duration in minutes before a call ends automatically.',
    )
    allow_audio_calls = models.BooleanField(default=True)
    allow_video_calls = models.BooleanField(default=True)
    allow_screen_share = models.BooleanField(default=True)
    allow_in_call_chat = models.BooleanField(default=True)
    allow_waiting_room = models.BooleanField(default=True)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_call_settings',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calling_platform_settings'
        verbose_name = 'Platform Call Settings'
        verbose_name_plural = 'Platform Call Settings'

    def __str__(self):
        state = 'Enabled' if self.calling_enabled else 'Disabled'
        return f'Platform Calling ({state}, max {self.max_participants} users)'

    @classmethod
    def get_solo(cls):
        """Return the singleton settings row, creating defaults if missing."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class RoleCallPermission(models.Model):
    """
    Default calling permissions per user role (e.g. 'user', 'teacher', 'admin').
    """

    ROLE_CHOICES = [
        ('user', 'User / Learner'),
        ('teacher', 'Teacher / Mentor'),
        ('admin', 'Admin'),
    ]

    role_name = models.CharField(max_length=30, unique=True, choices=ROLE_CHOICES)
    can_call = models.BooleanField(default=True)
    can_host = models.BooleanField(default=True)
    can_screen_share = models.BooleanField(default=True)
    can_create_group_call = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calling_role_permissions'
        ordering = ['role_name']
        verbose_name = 'Role Call Permission'
        verbose_name_plural = 'Role Call Permissions'

    def __str__(self):
        return f'Role: {self.role_name}'


class UserCallPermission(models.Model):
    """
    Per-user calling overrides and block/unblock enforcement.
    Nullable boolean fields inherit from the user's RoleCallPermission when None.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='call_permission',
    )
    is_blocked_from_calling = models.BooleanField(
        default=False,
        help_text='If True, this user cannot initiate, receive, or join calls.',
    )
    block_reason = models.CharField(max_length=255, blank=True, default='')

    can_call = models.BooleanField(null=True, blank=True)
    can_host = models.BooleanField(null=True, blank=True)
    can_screen_share = models.BooleanField(null=True, blank=True)
    can_create_group_call = models.BooleanField(null=True, blank=True)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_permissions_modified',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calling_user_permissions'
        verbose_name = 'User Call Permission'
        verbose_name_plural = 'User Call Permissions'

    def __str__(self):
        flag = ' [BLOCKED]' if self.is_blocked_from_calling else ''
        return f'{self.user.username}{flag}'


class CallRoom(models.Model):
    """
    Tracks active and completed WebRTC call rooms hosted on the self-hosted SFU.
    """

    CALL_KIND_CHOICES = [
        ('one_to_one', 'One-to-One'),
        ('group', 'Group Call'),
        ('batch', 'Batch Class'),
        ('doubt', 'Doubt Session'),
    ]

    MEDIA_TYPE_CHOICES = [
        ('audio', 'Audio Only'),
        ('video', 'Audio & Video'),
    ]

    room_code = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=200, default='Skill-Verse Call')
    call_kind = models.CharField(
        max_length=20, choices=CALL_KIND_CHOICES, default='one_to_one'
    )
    media_type = models.CharField(
        max_length=10, choices=MEDIA_TYPE_CHOICES, default='video'
    )
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hosted_call_rooms',
    )
    max_participants = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(2), MaxValueValidator(10)],
    )
    is_locked = models.BooleanField(default=False)
    waiting_room_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    ended_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ended_call_rooms',
    )

    class Meta:
        db_table = 'calling_rooms'
        ordering = ['-started_at']
        verbose_name = 'Call Room'
        verbose_name_plural = 'Call Rooms'

    def __str__(self):
        status = 'Active' if self.is_active else 'Ended'
        return f'{self.room_code} ({self.title}) [{status}]'

    @property
    def duration_seconds(self):
        end = self.ended_at or timezone.now()
        return max(0, int((end - self.started_at).total_seconds()))


class CallLog(models.Model):
    """
    Call history record for callers, receivers, and platform admins.
    """

    CALL_TYPE_CHOICES = [
        ('audio', 'Audio Call'),
        ('video', 'Video Call'),
        ('group', 'Group Call'),
    ]

    STATUS_CHOICES = [
        ('ringing', 'Ringing'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('declined', 'Declined'),
        ('busy', 'Busy'),
        ('cancelled', 'Cancelled'),
        ('ended_by_admin', 'Ended by Admin'),
    ]

    room = models.ForeignKey(
        CallRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    caller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='outgoing_call_logs',
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_call_logs',
    )
    call_type = models.CharField(max_length=12, choices=CALL_TYPE_CHOICES, default='video')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ringing', db_index=True
    )

    started_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'calling_logs'
        ordering = ['-started_at']
        verbose_name = 'Call Log'
        verbose_name_plural = 'Call Logs'

    def __str__(self):
        target = self.receiver.username if self.receiver else 'Group'
        return f'{self.caller.username} -> {target} ({self.call_type}, {self.status})'

    def finalize(self, final_status, ended_at=None):
        """Mark the call log finished and compute elapsed duration when answered."""
        end_time = ended_at or timezone.now()
        self.status = final_status
        self.ended_at = end_time
        if self.answered_at:
            self.duration_seconds = max(0, int((end_time - self.answered_at).total_seconds()))
        else:
            self.duration_seconds = 0
        self.save(update_fields=['status', 'ended_at', 'duration_seconds'])


class CallAuditLog(models.Model):
    """
    Immutable audit trail for every calling-related admin action.
    """

    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='call_audit_logs',
    )
    action = models.CharField(max_length=200)
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='targeted_call_audit_logs',
    )
    target_room_code = models.CharField(max_length=64, blank=True, default='')
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'calling_audit_logs'
        ordering = ['-created_at']
        verbose_name = 'Call Audit Log'
        verbose_name_plural = 'Call Audit Logs'

    def __str__(self):
        actor = self.admin.username if self.admin else 'System'
        return f'[{self.created_at:%Y-%m-%d %H:%M}] {actor}: {self.action}'
