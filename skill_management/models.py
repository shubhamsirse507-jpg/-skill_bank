"""
skill_management/models.py
Canonical SkillCategory + Skill models — the single source of truth for the platform.
Replaces: user_dashboard.Skill, admin_panel.SkillCategory/PlatformSkill, old skill_management models.
Matches spec Table 7: skill_categories + skills tables exactly.
"""

from django.db import models
from django.contrib.auth.models import User


class SkillCategory(models.Model):
    """
    Spec table: skill_categories
    Fields: category_name (spec name), description, status + extras from admin_panel version.
    """

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    # Spec exact field name
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')

    # Spec status field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    # Extras kept from admin_panel.SkillCategory (useful UI additions)
    icon_class = models.CharField(
        max_length=80, default='fa-solid fa-layer-group',
        help_text='FontAwesome icon class'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skill_categories'
        verbose_name = 'Skill Category'
        verbose_name_plural = 'Skill Categories'
        ordering = ['category_name']

    def __str__(self):
        return self.category_name


class Skill(models.Model):
    """
    Spec table: skills
    Fields: user_id (FK), category_id (FK), title, description,
            skill_type (offered/wanted), level, status (pending/approved/rejected), created_at.
    ALL fields were missing from at least one of the three duplicate models.
    """

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    SKILL_TYPE_CHOICES = [
        ('offered', 'Offered'),
        ('wanted', 'Wanted'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Spec: user_id FK — was MISSING from ALL three duplicate versions
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='skills',
        help_text='User who owns this skill listing'
    )
    # Spec: category_id FK
    category = models.ForeignKey(
        SkillCategory, on_delete=models.CASCADE, related_name='skills'
    )
    # Spec: title
    title = models.CharField(max_length=150)
    # Spec: description
    description = models.TextField(blank=True, default='')
    # Spec: skill_type — was MISSING everywhere
    skill_type = models.CharField(
        max_length=10, choices=SKILL_TYPE_CHOICES, default='offered'
    )
    # Spec: level
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    # Spec: status — was MISSING everywhere
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    # Spec: created_at
    created_at = models.DateTimeField(auto_now_add=True)

    # Extra from admin_panel.PlatformSkill — useful for admin UI, kept
    demand_level = models.CharField(
        max_length=10,
        choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')],
        default='MEDIUM'
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'skills'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_skill_type_display()}) — {self.user.username}"