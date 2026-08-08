"""
admin_panel/models.py
Spec tables: reports, admin_logs, platform_notices.
Removed duplicate SkillCategory and PlatformSkill (moved to skill_management).
Updated field names: reporter -> reported_by, details -> description, actor -> admin_id, target -> target_table + target_id.
"""

from django.db import models
from django.contrib.auth.models import User


class PlatformReport(models.Model):
    """
    Spec table: reports
    Platform moderation reports.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('IN_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]

    REASON_CHOICES = [
        ('SPAM', 'Spam or Unsolicited Promotion'),
        ('HARASSMENT', 'Harassment or Abusive Behavior'),
        ('FAKE_PROFILE', 'Fake Profile or Misrepresentation'),
        ('INAPPROPRIATE', 'Inappropriate Content'),
        ('OTHER', 'Other Violation'),
    ]

    # Spec: reported_by (was: reporter)
    reported_by = models.ForeignKey(
        User, related_name='submitted_reports', on_delete=models.CASCADE
    )
    reported_user = models.ForeignKey(
        User, related_name='reports_against', on_delete=models.CASCADE,
        null=True, blank=True
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default='OTHER')
    # Spec: description (was: details)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    action_taken = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} - {self.get_reason_display()} ({self.status})"


class PlatformNotice(models.Model):
    """Platform system announcements broadcast to users."""

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    TARGET_CHOICES = [
        ('ALL', 'All Users'),
        ('TEACHERS', 'Mentors / Teachers'),
        ('LEARNERS', 'Learners'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    target_group = models.CharField(max_length=20, choices=TARGET_CHOICES, default='ALL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'platform_notices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notice: {self.title} [{self.priority}]"


class AuditLog(models.Model):
    """
    Spec table: admin_logs
    Audit logging for admin actions.
    """

    # Spec: admin_id (was: actor)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=200)
    # Spec: split target into target_table and target_id
    target_table = models.CharField(max_length=100, blank=True, default='')
    target_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.admin} - {self.action}"
