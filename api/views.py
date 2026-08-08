"""
api/views.py
REST API views for /api/v1/ endpoints.
Supports mobile clients and SPA frontends with JWT authentication.
"""

from rest_framework import status, generics, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
import random
from datetime import timedelta
from django.utils import timezone

from skill_bank.utils import api_error, api_success
from authentication.models import OTPVerification
from profiles.models import UserProfile
from skill_management.models import SkillCategory, Skill
from messaging.models import SkillExchange, Conversation, Message
from bookings.models import Booking
from ratings.models import ReviewRating
from notifications.models import Notification
from admin_panel.models import PlatformReport, PlatformNotice, AuditLog

from .serializers import (
    UserSerializer, UserProfileSerializer, SkillCategorySerializer,
    SkillSerializer, SkillExchangeSerializer, ConversationSerializer,
    MessageSerializer, BookingSerializer, ReviewRatingSerializer,
    NotificationSerializer, PlatformReportSerializer, PlatformNoticeSerializer,
    AuditLogSerializer
)


# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        phone = request.data.get('phone', '').strip()

        if not username or not email or not password:
            return api_error('missing_fields', 'Username, email, and password are required.')

        if User.objects.filter(username__iexact=username).exists():
            return api_error('duplicate_username', 'Username is already taken.')

        if User.objects.filter(email__iexact=email).exists():
            return api_error('duplicate_email', 'An account with this email already exists.')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )

        profile = UserProfile.objects.create(user=user, phone=phone)

        refresh = RefreshToken.for_user(user)
        return api_success({
            'message': 'User registered successfully.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status_code=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username_or_email or not password:
            return api_error('missing_credentials', 'Both username/email and password are required.')

        user_obj = User.objects.filter(email__iexact=username_or_email).first()
        username = user_obj.username if user_obj else username_or_email

        user = authenticate(request, username=username, password=password)
        if not user:
            return api_error('invalid_credentials', 'Invalid username/email or password.', status_code=401)

        if not user.is_active:
            return api_error('account_inactive', 'Account has been deactivated or suspended.', status_code=403)

        refresh = RefreshToken.for_user(user)
        return api_success({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ProfileMeAPIView(APIView):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return api_success(UserProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_success(serializer.data)
        return api_error('validation_error', 'Invalid profile data.', details=serializer.errors)


# ---------------------------------------------------------------------------
# Skills API
# ---------------------------------------------------------------------------
class SkillCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SkillCategory.objects.filter(is_active=True)
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.AllowAny]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.filter(status='approved')
    serializer_class = SkillSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Skill.objects.all()
        category = self.request.query_params.get('category')
        skill_type = self.request.query_params.get('type')
        query = self.request.query_params.get('q')

        if category:
            qs = qs.filter(category_id=category)
        if skill_type:
            qs = qs.filter(skill_type=skill_type)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='approved')


# ---------------------------------------------------------------------------
# Skill Exchanges & Messaging API
# ---------------------------------------------------------------------------
class SkillExchangeViewSet(viewsets.ModelViewSet):
    serializer_class = SkillExchangeSerializer

    def get_queryset(self):
        user = self.request.user
        return SkillExchange.objects.filter(
            Q(requester=user) | Q(receiver=user)
        ).select_related('requester', 'receiver', 'skill').order_by('-updated_at')

    def perform_create(self, serializer):
        exchange = serializer.save(requester=self.request.user, status='pending')
        Conversation.objects.get_or_create(
            request=exchange,
            defaults={'user_one': exchange.requester, 'user_two': exchange.receiver}
        )


class MessageListCreateAPIView(APIView):
    def get(self, request, exchange_id):
        exchange = get_object_or_404(
            SkillExchange.objects.filter(Q(requester=request.user) | Q(receiver=request.user)),
            id=exchange_id
        )
        conversation, _ = Conversation.objects.get_or_create(
            request=exchange,
            defaults={'user_one': exchange.requester, 'user_two': exchange.receiver}
        )
        messages_qs = conversation.messages.select_related('sender').all()
        return api_success(MessageSerializer(messages_qs, many=True).data)

    def post(self, request, exchange_id):
        exchange = get_object_or_404(
            SkillExchange.objects.filter(Q(requester=request.user) | Q(receiver=request.user)),
            id=exchange_id
        )
        conversation, _ = Conversation.objects.get_or_create(
            request=exchange,
            defaults={'user_one': exchange.requester, 'user_two': exchange.receiver}
        )
        message_text = request.data.get('message_text', '').strip()
        if not message_text:
            return api_error('empty_message', 'message_text is required.')

        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_text=message_text
        )
        exchange.save()
        return api_success(MessageSerializer(msg).data, status_code=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Bookings API
# ---------------------------------------------------------------------------
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        user_exchanges = SkillExchange.objects.filter(Q(requester=user) | Q(receiver=user))
        return Booking.objects.filter(request__in=user_exchanges).order_by('-scheduled_date')


# ---------------------------------------------------------------------------
# Ratings API
# ---------------------------------------------------------------------------
class ReviewRatingViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewRatingSerializer

    def get_queryset(self):
        return ReviewRating.objects.select_related('reviewer', 'reviewed_user', 'booking').all()

    def perform_create(self, serializer):
        booking = serializer.validated_data['booking']
        reviewer = self.request.user
        reviewed_user = booking.request.receiver if reviewer == booking.request.requester else booking.request.requester
        serializer.save(reviewer=reviewer, reviewed_user=reviewed_user)


# ---------------------------------------------------------------------------
# Notifications API
# ---------------------------------------------------------------------------
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


# ---------------------------------------------------------------------------
# Admin API (Staff only)
# ---------------------------------------------------------------------------
class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class AdminReportViewSet(viewsets.ModelViewSet):
    serializer_class = PlatformReportSerializer
    permission_classes = [IsStaffUser]
    queryset = PlatformReport.objects.all()
