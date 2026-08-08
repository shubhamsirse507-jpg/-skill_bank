"""
api/urls.py
URL routing for REST API v1.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView, LoginAPIView, ProfileMeAPIView,
    SkillCategoryViewSet, SkillViewSet, SkillExchangeViewSet,
    MessageListCreateAPIView, BookingViewSet, ReviewRatingViewSet,
    NotificationViewSet, AdminReportViewSet
)

router = DefaultRouter()
router.register(r'categories', SkillCategoryViewSet, basename='category')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'exchanges', SkillExchangeViewSet, basename='exchange')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'ratings', ReviewRatingViewSet, basename='rating')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'admin/reports', AdminReportViewSet, basename='admin-report')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('profile/me/', ProfileMeAPIView.as_view(), name='api_profile_me'),

    # Messaging detail messages
    path('exchanges/<int:exchange_id>/messages/', MessageListCreateAPIView.as_view(), name='api_exchange_messages'),

    # ViewSets
    path('', include(router.urls)),
]
