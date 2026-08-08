"""
authentication/models.py
OTPVerification — stores one-time passwords for registration, login, and password reset.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class OTPVerification(models.Model):
    """Stores OTP codes for email-based verification flows."""

    PURPOSE_CHOICES = [
        ('Registration', 'Registration'),
        ('Login', 'Login'),
        ('ForgotPassword', 'Forgot Password'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_verifications',
    )
    otp_code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP Verification'

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP({self.purpose}) for {self.user.username} — {'verified' if self.is_verified else 'pending'}"
