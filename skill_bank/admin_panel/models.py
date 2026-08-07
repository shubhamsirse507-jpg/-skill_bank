from django.db import models
from django.contrib.auth.models import User


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, default='fa-solid fa-layer-group', help_text="FontAwesome icon class")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Skill Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class PlatformSkill(models.Model):
    DEMAND_CHOICES = [
        ('HIGH', 'High Demand'),
        ('MEDIUM', 'Medium Demand'),
        ('LOW', 'Low Demand'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(SkillCategory, related_name='skills', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    demand_level = models.CharField(max_length=20, choices=DEMAND_CHOICES, default='MEDIUM')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class PlatformReport(models.Model):
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

    reporter = models.ForeignKey(User, related_name='submitted_reports', on_delete=models.CASCADE)
    reported_user = models.ForeignKey(User, related_name='reports_against', on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default='OTHER')
    details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    action_taken = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} - {self.get_reason_display()} ({self.status})"


class PlatformNotice(models.Model):
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
        ordering = ['-created_at']

    def __str__(self):
        return f"Notice: {self.title} [{self.priority}]"


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.actor} - {self.action}"
