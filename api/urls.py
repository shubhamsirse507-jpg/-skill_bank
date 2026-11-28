"""
api/urls.py
URL routing for REST API v1.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView, LoginAPIView, Verify2FAAPIView,
    ForgotPasswordAPIView, VerifyOTPAPIView, ResetPasswordAPIView,
    ProfileMeAPIView,
    SkillCategoryViewSet, SkillViewSet, SkillExchangeViewSet,
    MessageListCreateAPIView, BookingViewSet, ReviewRatingViewSet,
    NotificationViewSet, AdminReportViewSet, SkillCertificateViewSet
)

router = SimpleRouter()

router.register(r'categories', SkillCategoryViewSet, basename='category')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'exchanges', SkillExchangeViewSet, basename='exchange')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'ratings', ReviewRatingViewSet, basename='rating')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'certificates', SkillCertificateViewSet, basename='certificate')
router.register(r'admin/reports', AdminReportViewSet, basename='admin-report')

urlpatterns = [
    # Auth & 2FA & OTP
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/verify-2fa/', Verify2FAAPIView.as_view(), name='api_verify_2fa'),
    path('auth/forgot-password/', ForgotPasswordAPIView.as_view(), name='api_forgot_password'),
    path('auth/verify-otp/', VerifyOTPAPIView.as_view(), name='api_verify_otp'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='api_reset_password'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('profile/me/', ProfileMeAPIView.as_view(), name='api_profile_me'),

    # Messaging detail messages
    path('exchanges/<int:exchange_id>/messages/', MessageListCreateAPIView.as_view(), name='api_exchange_messages'),

    # Self-hosted WebRTC calling integration (Phase B+)
    path('calling/', include('calling.urls')),

    # ViewSets
    path('', include(router.urls)),
]
