import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    CallAuditLog,
    CallLog,
    CallRoom,
    PlatformCallSettings,
    RoleCallPermission,
    UserCallPermission,
)
from .services import record_call_audit


@admin.register(PlatformCallSettings)
class PlatformCallSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'calling_enabled',
        'max_participants',
        'max_call_duration_minutes',
        'allow_audio_calls',
        'allow_video_calls',
        'allow_screen_share',
        'allow_in_call_chat',
        'updated_by',
        'updated_at',
    )
    readonly_fields = ('updated_by', 'updated_at')

    def has_add_permission(self, request):
        return not PlatformCallSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        record_call_audit(
            request.user,
            'Updated PlatformCallSettings',
            details={
                'calling_enabled': obj.calling_enabled,
                'max_participants': obj.max_participants,
                'max_call_duration_minutes': obj.max_call_duration_minutes,
                'allow_screen_share': obj.allow_screen_share,
                'allow_in_call_chat': obj.allow_in_call_chat,
            },
        )


@admin.register(RoleCallPermission)
class RoleCallPermissionAdmin(admin.ModelAdmin):
    list_display = (
        'role_name',
        'can_call',
        'can_host',
        'can_screen_share',
        'can_create_group_call',
        'updated_at',
    )
    list_editable = ('can_call', 'can_host', 'can_screen_share', 'can_create_group_call')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        record_call_audit(
            request.user,
            f'Updated RoleCallPermission for role "{obj.role_name}"',
            details={
                'can_call': obj.can_call,
                'can_host': obj.can_host,
                'can_screen_share': obj.can_screen_share,
                'can_create_group_call': obj.can_create_group_call,
            },
        )


@admin.register(UserCallPermission)
class UserCallPermissionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'is_blocked_from_calling',
        'can_call',
        'can_host',
        'can_screen_share',
        'can_create_group_call',
        'updated_by',
        'updated_at',
    )
    list_filter = ('is_blocked_from_calling', 'can_call', 'can_host', 'can_screen_share')
    search_fields = ('user__username', 'user__email', 'block_reason')
    readonly_fields = ('updated_by', 'updated_at')
    actions = ('block_from_calling', 'unblock_from_calling')

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        record_call_audit(
            request.user,
            f'Updated UserCallPermission for {obj.user.username}',
            target_user=obj.user,
            details={'is_blocked_from_calling': obj.is_blocked_from_calling},
        )

    @admin.action(description='Block selected users from calling')
    def block_from_calling(self, request, queryset):
        for perm in queryset.select_related('user'):
            perm.is_blocked_from_calling = True
            perm.updated_by = request.user
            perm.save(update_fields=['is_blocked_from_calling', 'updated_by', 'updated_at'])
            record_call_audit(
                request.user,
                f'Blocked {perm.user.username} from calling',
                target_user=perm.user,
            )

    @admin.action(description='Unblock selected users from calling')
    def unblock_from_calling(self, request, queryset):
        for perm in queryset.select_related('user'):
            perm.is_blocked_from_calling = False
            perm.block_reason = ''
            perm.updated_by = request.user
            perm.save(update_fields=['is_blocked_from_calling', 'block_reason', 'updated_by', 'updated_at'])
            record_call_audit(
                request.user,
                f'Unblocked {perm.user.username} for calling',
                target_user=perm.user,
            )


@admin.register(CallRoom)
class CallRoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_code',
        'title',
        'call_kind',
        'media_type',
        'host',
        'max_participants',
        'is_active',
        'is_locked',
        'started_at',
        'duration_seconds',
    )
    list_filter = ('is_active', 'is_locked', 'call_kind', 'media_type', 'waiting_room_enabled')
    search_fields = ('room_code', 'title', 'host__username')
    readonly_fields = ('started_at',)
    actions = ('mark_rooms_ended',)

    @admin.action(description='End selected active call rooms')
    def mark_rooms_ended(self, request, queryset):
        now = timezone.now()
        for room in queryset.filter(is_active=True):
            room.is_active = False
            room.ended_at = now
            room.ended_by = request.user
            room.save(update_fields=['is_active', 'ended_at', 'ended_by'])
            record_call_audit(
                request.user,
                f'Ended CallRoom {room.room_code} via Django Admin',
                target_room_code=room.room_code,
            )


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'caller',
        'receiver',
        'call_type',
        'status',
        'started_at',
        'ended_at',
        'duration_seconds',
    )
    list_filter = ('status', 'call_type', 'started_at')
    search_fields = ('caller__username', 'receiver__username', 'room__room_code', 'notes')
    readonly_fields = ('started_at',)
    actions = ('export_call_logs_csv',)

    @admin.action(description='Export selected call logs to CSV')
    def export_call_logs_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="skillverse_call_logs.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID',
            'Room Code',
            'Caller',
            'Receiver',
            'Call Type',
            'Status',
            'Started At',
            'Answered At',
            'Ended At',
            'Duration (s)',
            'Notes',
        ])

        for log in queryset.select_related('caller', 'receiver', 'room'):
            writer.writerow([
                log.id,
                log.room.room_code if log.room else '',
                log.caller.username,
                log.receiver.username if log.receiver else '',
                log.call_type,
                log.status,
                log.started_at.isoformat() if log.started_at else '',
                log.answered_at.isoformat() if log.answered_at else '',
                log.ended_at.isoformat() if log.ended_at else '',
                log.duration_seconds,
                log.notes,
            ])

        record_call_audit(
            request.user,
            f'Exported {queryset.count()} call log(s) to CSV',
        )
        return response


@admin.register(CallAuditLog)
class CallAuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'admin', 'action', 'target_user', 'target_room_code')
    list_filter = ('created_at',)
    search_fields = ('admin__username', 'action', 'target_user__username', 'target_room_code')
    readonly_fields = ('admin', 'action', 'target_user', 'target_room_code', 'details', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
