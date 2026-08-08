"""
profiles/models.py
UserProfile — one-to-one extension of Django's auth.User.
Matches spec table: users (phone, status, role) + user_profiles (bio, location, etc.)
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user data. Created automatically on user registration."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
    ]

    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]

    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('weekends_only', 'Weekends Only'),
        ('not_available', 'Not Available'),
    ]

    # Spec fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=200, blank=True, default='')
    profile_image = models.ImageField(
        upload_to='profile_photos/', null=True, blank=True
    )
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default='available'
    )
    experience_summary = models.TextField(blank=True, default='')

    # Spec's users table extras
    phone = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # UI extras (from existing profiles/views.py session data — preserved)
    headline = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    work_preference = models.CharField(max_length=50, blank=True, default='Remote')
    matching_goal = models.CharField(max_length=100, blank=True, default='Peer Skill Swap')

    # Avatar (preset URL or uploaded file)
    avatar_preset_url = models.URLField(
        blank=True,
        default='https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero'
    )

    # Privacy
    show_email = models.BooleanField(default=True)
    show_phone = models.BooleanField(default=False)
    is_profile_public = models.BooleanField(default=True)

    # Resume
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def avatar_url(self):
        if self.profile_image:
            return self.profile_image.url
        return self.avatar_preset_url
