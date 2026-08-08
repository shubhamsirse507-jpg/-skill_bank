from django.contrib import admin
from .models import OTPVerification


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'purpose', 'is_verified', 'expires_at', 'created_at')
    list_filter = ('purpose', 'is_verified')
    search_fields = ('user__username', 'user__email', 'otp_code')
