from django.contrib import admin
from .models import PlatformReport, PlatformNotice, AuditLog, TeacherMockTest


@admin.register(PlatformReport)
class PlatformReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reported_by', 'reported_user', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
    search_fields = ('reported_by__username', 'reported_user__username', 'description')


@admin.register(PlatformNotice)
class PlatformNoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'priority', 'target_group', 'is_active', 'created_at')
    list_filter = ('priority', 'target_group', 'is_active')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'admin', 'action', 'target_table', 'target_id', 'created_at')
    list_filter = ('target_table',)
    search_fields = ('admin__username', 'action')


@admin.register(TeacherMockTest)
class TeacherMockTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'skill_name', 'skill_level', 'score', 'total_questions', 'percentage', 'status', 'created_at')
    list_filter = ('status', 'skill_level', 'created_at')
    search_fields = ('teacher__username', 'teacher__email', 'skill_name', 'admin_notes')
    ordering = ('-created_at',)

