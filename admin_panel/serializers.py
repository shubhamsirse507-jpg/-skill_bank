"""
admin_panel/serializers.py
DRF serializers for PlatformReport, PlatformNotice, AuditLog.
"""
from rest_framework import serializers
from .models import PlatformReport, PlatformNotice, AuditLog


class PlatformReportSerializer(serializers.ModelSerializer):
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    reported_user_username = serializers.CharField(source='reported_user.username', read_only=True)

    class Meta:
        model = PlatformReport
        fields = [
            'id', 'reported_by', 'reported_by_username',
            'reported_user', 'reported_user_username',
            'reason', 'description', 'status', 'action_taken',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'reported_by', 'created_at', 'updated_at']


class PlatformNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformNotice
        fields = ['id', 'title', 'message', 'priority', 'target_group', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'admin', 'admin_username', 'action', 'target_table', 'target_id', 'created_at']
        read_only_fields = ['id', 'created_at']
