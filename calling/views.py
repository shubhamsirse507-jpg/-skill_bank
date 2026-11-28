from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from django.conf import settings
from django.db.models import Q

from .models import CallLog, PlatformCallSettings
from .services import get_effective_call_permissions


def serialize_user_summary(user):
    profile = getattr(user, 'profile', None)
    return {
        'id': user.id,
        'username': user.username,
        'name': user.get_full_name() or user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'avatar_url': profile.avatar_url if profile else '',
    }


def serialize_call_settings(cfg):
    return {
        'calling_enabled': cfg.calling_enabled,
        'max_participants': min(cfg.max_participants, 10),
        'max_call_duration_minutes': cfg.max_call_duration_minutes,
        'allow_audio_calls': cfg.allow_audio_calls,
        'allow_video_calls': cfg.allow_video_calls,
        'allow_screen_share': cfg.allow_screen_share,
        'allow_in_call_chat': cfg.allow_in_call_chat,
        'allow_waiting_room': cfg.allow_waiting_room,
        'updated_at': cfg.updated_at.isoformat() if cfg.updated_at else None,
    }


class CallingSessionTokenAPIView(APIView):
    """
    GET /api/v1/calling/token/
    Issues a Django SimpleJWT access token (signed with settings.SECRET_KEY)
    and live server-computed calling permissions for the logged-in user.
    Supports both Django session cookies and Bearer SimpleJWT authentication.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        perms = get_effective_call_permissions(user)

        token = AccessToken.for_user(user)
        token['username'] = user.username
        token['name'] = user.get_full_name() or user.username
        token['email'] = user.email
        token['role'] = perms['role']
        token['is_staff'] = bool(user.is_staff)
        token['is_superuser'] = bool(user.is_superuser)

        return Response(
            {
                'token': str(token),
                'user': serialize_user_summary(user),
                'permissions': perms,
                'webrtc_server_url': getattr(settings, 'WEBRTC_SERVER_URL', 'http://localhost:4000'),
            },
            status=status.HTTP_200_OK,
        )


class CallingPermissionsAPIView(APIView):
    """
    GET /api/v1/calling/permissions/
    Returns live server-enforced calling permissions for the authenticated user.
    Used by both the frontend UI and the Node signaling/media server.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        perms = get_effective_call_permissions(user)
        return Response(
            {
                'user': serialize_user_summary(user),
                'permissions': perms,
            },
            status=status.HTTP_200_OK,
        )


class CallingSettingsAPIView(APIView):
    """
    GET /api/v1/calling/settings/
    Returns current platform-wide calling settings.
    Accepts either an authenticated user or the shared X-Internal-Secret from Node.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        internal_secret = getattr(settings, 'INTERNAL_CALLING_SECRET', '')
        provided_secret = request.headers.get('X-Internal-Secret', '')

        is_internal = bool(internal_secret and provided_secret == internal_secret)
        if not is_internal and not (request.user and request.user.is_authenticated):
            return Response(
                {'error': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        cfg = PlatformCallSettings.get_solo()
        return Response({'settings': serialize_call_settings(cfg)}, status=status.HTTP_200_OK)


class MyCallLogsAPIView(APIView):
    """
    GET /api/v1/calling/logs/
    Returns the authenticated user's own call history (outgoing + incoming).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = (
            CallLog.objects.filter(Q(caller=request.user) | Q(receiver=request.user))
            .select_related('caller', 'receiver', 'room')
            .order_by('-started_at')[:50]
        )

        items = []
        for log in logs:
            items.append(
                {
                    'id': log.id,
                    'room_code': log.room.room_code if log.room else '',
                    'caller_id': log.caller_id,
                    'caller_username': log.caller.username,
                    'caller_name': log.caller.get_full_name() or log.caller.username,
                    'receiver_id': log.receiver_id,
                    'receiver_username': log.receiver.username if log.receiver else None,
                    'receiver_name': (
                        (log.receiver.get_full_name() or log.receiver.username)
                        if log.receiver
                        else 'Group Call'
                    ),
                    'call_type': log.call_type,
                    'status': log.status,
                    'started_at': log.started_at.isoformat() if log.started_at else None,
                    'answered_at': log.answered_at.isoformat() if log.answered_at else None,
                    'ended_at': log.ended_at.isoformat() if log.ended_at else None,
                    'duration_seconds': log.duration_seconds,
                    'direction': 'outgoing' if log.caller_id == request.user.id else 'incoming',
                }
            )

        return Response({'logs': items}, status=status.HTTP_200_OK)
