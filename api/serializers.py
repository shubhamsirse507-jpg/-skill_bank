"""
api/serializers.py
DRF Serializers for every module in the Skill Exchange Platform API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from profiles.models import UserProfile
from skill_management.models import SkillCategory, Skill
from messaging.models import SkillExchange, Conversation, Message
from bookings.models import Booking
from ratings.models import ReviewRating
from notifications.models import Notification
from admin_panel.models import PlatformReport, PlatformNotice, AuditLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'location', 'profile_image', 'availability',
            'experience_summary', 'phone', 'status', 'role', 'headline',
            'city', 'country', 'work_preference', 'matching_goal',
            'avatar_preset_url', 'show_email', 'show_phone', 'is_profile_public'
        ]


class SkillCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillCategory
        fields = ['id', 'category_name', 'description', 'icon_class', 'status', 'is_active', 'created_at']


class SkillSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category_detail = SkillCategorySerializer(source='category', read_only=True)

    class Meta:
        model = Skill
        fields = [
            'id', 'user', 'category', 'category_detail', 'title', 'description',
            'skill_type', 'level', 'status', 'demand_level', 'is_featured', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class SkillExchangeSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    skill_detail = SkillSerializer(source='skill', read_only=True)

    class Meta:
        model = SkillExchange
        fields = [
            'id', 'requester', 'receiver', 'skill', 'skill_detail',
            'title', 'message', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['requester', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'message_text', 'is_read', 'has_attachment', 'attachment_name', 'created_at']
        read_only_fields = ['sender', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    user_one = UserSerializer(read_only=True)
    user_two = UserSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'request', 'user_one', 'user_two', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    request_detail = SkillExchangeSerializer(source='request', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'request', 'request_detail', 'scheduled_date', 'start_time',
            'end_time', 'meeting_mode', 'meeting_link', 'status', 'created_at'
        ]
        read_only_fields = ['created_at']


class ReviewRatingSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    reviewed_user = UserSerializer(read_only=True)

    class Meta:
        model = ReviewRating
        fields = [
            'id', 'booking', 'reviewer', 'reviewed_user', 'rating',
            'communication_rating', 'clarity_rating', 'punctuality_rating',
            'comment', 'tags', 'would_recommend', 'created_at'
        ]
        read_only_fields = ['reviewer', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'type', 'is_read',
            'action_url', 'action_text', 'sender_name', 'sender_avatar', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class PlatformReportSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer(read_only=True)
    reported_user_detail = UserSerializer(source='reported_user', read_only=True)

    class Meta:
        model = PlatformReport
        fields = [
            'id', 'reported_by', 'reported_user', 'reported_user_detail',
            'reason', 'description', 'status', 'action_taken', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reported_by', 'created_at', 'updated_at']


class PlatformNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformNotice
        fields = ['id', 'title', 'message', 'priority', 'target_group', 'is_active', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'admin', 'action', 'target_table', 'target_id', 'created_at']
