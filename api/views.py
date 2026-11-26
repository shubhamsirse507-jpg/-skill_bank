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
from skill_management.models import SkillCategory, Skill, SkillCertificate
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
    AuditLogSerializer, SkillCertificateSerializer
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

        profile, _ = UserProfile.objects.get_or_create(user=user)
        is_2fa = getattr(profile, 'two_factor_enabled', True)

        if is_2fa and user.email:
            otp = OTPVerification.generate_otp()
            expires = timezone.now() + timedelta(minutes=10)

            OTPVerification.objects.filter(
                user=user,
                purpose='Login',
                is_verified=False
            ).update(is_verified=True)

            OTPVerification.objects.create(
                user=user,
                otp_code=OTPVerification.hash_otp(otp),
                purpose='Login',
                expires_at=expires
            )

            # Send email
            from authentication.views import send_otp_email
            email_sent, sent_email = send_otp_email(user, otp, purpose='Login')
            if not email_sent:
                return api_error('email_send_failed', "We couldn't send the code. Please try again.", status_code=502)

            masked = OTPVerification.mask_email(sent_email)
            return api_success({
                'two_factor_required': True,
                'user_id': user.id,
                'email': masked,
                'message': f'A 6-digit code has been sent to {masked}.',
            })

        refresh = RefreshToken.for_user(user)
        return api_success({
            'two_factor_required': False,
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class Verify2FAAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        email = request.data.get('email', '').strip()
        otp = request.data.get('otp', '').strip()

        if not otp:
            return api_error('missing_otp', 'OTP code is required.')

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif email:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            return api_error('user_not_found', 'User not found.', status_code=404)

        otp_record = OTPVerification.objects.filter(
            user=user,
            purpose='Login',
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            return api_error('invalid_otp', 'No active 2FA code found.', status_code=400)

        if otp_record.is_expired():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            return api_error('expired_otp', '2FA code has expired.', status_code=400)

        if otp_record.is_locked():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            return api_error('otp_locked', 'Too many failed attempts. Please request a new code.', status_code=429)

        if not otp_record.verify_code(otp):
            otp_record.failed_attempts += 1
            if otp_record.failed_attempts >= OTPVerification.MAX_FAILED_ATTEMPTS:
                otp_record.is_verified = True
                otp_record.save(update_fields=['failed_attempts', 'is_verified'])
                return api_error('otp_locked', 'Too many failed attempts. Please request a new code.', status_code=429)
            otp_record.save(update_fields=['failed_attempts'])
            return api_error('invalid_otp', 'Invalid 2FA code.', status_code=400)

        otp_record.is_verified = True
        otp_record.save(update_fields=['is_verified'])

        refresh = RefreshToken.for_user(user)
        return api_success({
            'message': '2FA verification successful.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ForgotPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email_or_username = request.data.get('email', '').strip()
        if not email_or_username:
            return api_error('missing_email', 'Email or username is required.')

        user = User.objects.filter(email__iexact=email_or_username).first() or User.objects.filter(username__iexact=email_or_username).first()
        if not user:
            return api_error('user_not_found', 'No account found with this email or username.', status_code=404)

        OTPVerification.objects.filter(
            user=user,
            purpose='ForgotPassword',
            is_verified=False
        ).update(is_verified=True)

        otp = OTPVerification.generate_otp()
        expires = timezone.now() + timedelta(minutes=10)

        OTPVerification.objects.create(
            user=user,
            otp_code=OTPVerification.hash_otp(otp),
            purpose='ForgotPassword',
            expires_at=expires
        )

        from authentication.views import send_otp_email
        email_sent, sent_email = send_otp_email(user, otp, purpose='ForgotPassword')
        if not email_sent:
            return api_error('email_send_failed', "We couldn't send the code. Please try again.", status_code=502)

        masked = OTPVerification.mask_email(sent_email)
        return api_success({
            'message': f'A 6-digit code has been sent to {masked}.',
            'user_id': user.id,
            'email': masked,
        })


class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        email = request.data.get('email', '').strip()
        otp = request.data.get('otp', '').strip()

        if not otp:
            return api_error('missing_otp', 'OTP is required.')

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif email:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            return api_error('user_not_found', 'User not found.', status_code=404)

        otp_record = OTPVerification.objects.filter(
            user=user,
            purpose='ForgotPassword',
            is_verified=False
        ).order_by('-created_at').first()

        if not otp_record:
            return api_error('invalid_otp', 'Invalid OTP code.', status_code=400)

        if otp_record.is_expired():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            return api_error('expired_otp', 'OTP code has expired.', status_code=400)

        if otp_record.is_locked():
            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])
            return api_error('otp_locked', 'Too many failed attempts. Please request a new code.', status_code=429)

        if not otp_record.verify_code(otp):
            otp_record.failed_attempts += 1
            if otp_record.failed_attempts >= OTPVerification.MAX_FAILED_ATTEMPTS:
                otp_record.is_verified = True
                otp_record.save(update_fields=['failed_attempts', 'is_verified'])
                return api_error('otp_locked', 'Too many failed attempts. Please request a new code.', status_code=429)
            otp_record.save(update_fields=['failed_attempts'])
            return api_error('invalid_otp', 'Invalid OTP code.', status_code=400)

        otp_record.is_verified = True
        otp_record.save(update_fields=['is_verified'])

        return api_success({
            'message': 'OTP verified successfully.',
            'user_id': user.id,
            'verified': True
        })


class ResetPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        email = request.data.get('email', '').strip()
        otp = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '').strip()

        if not new_password or len(new_password) < 6:
            return api_error('invalid_password', 'New password must be at least 6 characters long.')

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif email:
            user = User.objects.filter(email__iexact=email).first()

        if not user:
            return api_error('user_not_found', 'User not found.', status_code=404)

        # Check for verified OTP within last 15 minutes
        cutoff = timezone.now() - timedelta(minutes=15)
        otp_record = OTPVerification.objects.filter(
            user=user,
            purpose='ForgotPassword',
            is_verified=True,
            created_at__gte=cutoff
        ).first()

        if not otp_record and not otp:
            return api_error('unauthorized', 'OTP verification is required before resetting password.', status_code=403)

        if not otp_record and otp:
            otp_record = OTPVerification.objects.filter(
                user=user,
                otp_code=otp,
                purpose='ForgotPassword'
            ).first()
            if not otp_record or otp_record.is_expired():
                return api_error('invalid_otp', 'Invalid or expired OTP.', status_code=400)

        user.set_password(new_password)
        user.save()

        return api_success({
            'message': 'Password reset successful. You can now log in with your new password.'
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


class SkillCertificateViewSet(viewsets.ModelViewSet):
    """
    API endpoint to list, view, and issue skill certificates.
    Users can view earned or issued certificates.
    """
    serializer_class = SkillCertificateSerializer

    def get_queryset(self):
        user = self.request.user
        return SkillCertificate.objects.filter(Q(student=user) | Q(teacher=user)).order_by('-issue_date')

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

