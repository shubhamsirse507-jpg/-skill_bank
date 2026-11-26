"""
authentication/models.py
OTPVerification — stores hashed one-time passwords for registration, login, and password reset.
"""

import hashlib
import hmac
import secrets
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class OTPVerification(models.Model):
    """Stores hashed OTP codes for email-based verification flows."""

    MAX_FAILED_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 30

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
    otp_code = models.CharField(max_length=128)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP Verification'

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_locked(self):
        return self.failed_attempts >= self.MAX_FAILED_ATTEMPTS

    @staticmethod
    def generate_otp():
        """Cryptographically secure 6-digit OTP."""
        return f"{100000 + secrets.randbelow(900000)}"

    @staticmethod
    def hash_otp(otp_code: str) -> str:
        """Return HMAC-SHA256 hex digest of the OTP keyed with SECRET_KEY."""
        key = str(settings.SECRET_KEY).encode('utf-8')
        msg = str(otp_code).strip().encode('utf-8')
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email like a***n@skillbank.com."""
        email = (email or '').strip()
        if '@' not in email:
            return email
        local, domain = email.split('@', 1)
        if len(local) <= 1:
            masked_local = '*'
        elif len(local) == 2:
            masked_local = f"{local[0]}*"
        else:
            masked_local = f"{local[0]}{'*' * min(len(local) - 2, 3)}{local[-1]}"
        return f"{masked_local}@{domain}"

    def verify_code(self, submitted_otp: str) -> bool:
        """Constant-time comparison against stored HMAC-SHA256 hash."""
        submitted_hash = self.hash_otp(submitted_otp)
        return hmac.compare_digest(self.otp_code, submitted_hash)

    def __str__(self):
        return f"OTP({self.purpose}) for {self.user.username} — {'verified' if self.is_verified else 'pending'}"
