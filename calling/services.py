from admin_panel.models import AuditLog

from .models import (
    CallAuditLog,
    PlatformCallSettings,
    RoleCallPermission,
    UserCallPermission,
)


def resolve_user_role_name(user):
    """
    Map a Django User + UserProfile to the canonical calling role name.
    """
    if not user or not user.is_authenticated:
        return 'user'

    profile = getattr(user, 'profile', None)
    if user.is_superuser or user.is_staff or (profile and profile.role == 'admin'):
        return 'admin'

    # Users who instruct batches or have approved mock tests act as teachers.
    if hasattr(user, 'batches') and user.batches.exists():
        return 'teacher'

    return 'user'


def get_effective_call_permissions(user):
    """
    Compute server-enforced calling permissions for a given user by merging
    global PlatformCallSettings, RoleCallPermission, and UserCallPermission overrides.
    """
    settings_obj = PlatformCallSettings.get_solo()
    role_name = resolve_user_role_name(user)

    role_perm, _ = RoleCallPermission.objects.get_or_create(
        role_name=role_name,
        defaults={
            'can_call': True,
            'can_host': True,
            'can_screen_share': True,
            'can_create_group_call': True,
        },
    )

    user_perm = UserCallPermission.objects.filter(user=user).first()
    is_blocked = bool(user_perm and user_perm.is_blocked_from_calling)

    def resolve_flag(override_val, role_val):
        return bool(role_val if override_val is None else override_val)

    can_call = (
        settings_obj.calling_enabled
        and not is_blocked
        and resolve_flag(user_perm.can_call if user_perm else None, role_perm.can_call)
    )
    can_host = (
        can_call
        and resolve_flag(user_perm.can_host if user_perm else None, role_perm.can_host)
    )
    can_screen_share = (
        can_call
        and settings_obj.allow_screen_share
        and resolve_flag(
            user_perm.can_screen_share if user_perm else None,
            role_perm.can_screen_share,
        )
    )
    can_create_group_call = (
        can_call
        and resolve_flag(
            user_perm.can_create_group_call if user_perm else None,
            role_perm.can_create_group_call,
        )
    )

    return {
        'calling_enabled': settings_obj.calling_enabled,
        'is_blocked': is_blocked,
        'block_reason': user_perm.block_reason if is_blocked else '',
        'role': role_name,
        'can_call': can_call,
        'can_host': can_host,
        'can_screen_share': can_screen_share,
        'can_create_group_call': can_create_group_call,
        'allow_audio_calls': settings_obj.allow_audio_calls,
        'allow_video_calls': settings_obj.allow_video_calls,
        'allow_in_call_chat': settings_obj.allow_in_call_chat,
        'allow_waiting_room': settings_obj.allow_waiting_room,
        'max_participants': min(settings_obj.max_participants, 10),
        'max_call_duration_minutes': settings_obj.max_call_duration_minutes,
    }


def record_call_audit(admin_user, action, target_user=None, target_room_code='', details=None):
    """
    Record an admin calling action in both CallAuditLog and admin_panel.AuditLog.
    """
    entry = CallAuditLog.objects.create(
        admin=admin_user,
        action=action,
        target_user=target_user,
        target_room_code=target_room_code or '',
        details=details or {},
    )
    AuditLog.objects.create(
        admin=admin_user,
        action=f'[Calling] {action}',
        target_table='calling',
        target_id=target_user.id if target_user else None,
    )
    return entry
