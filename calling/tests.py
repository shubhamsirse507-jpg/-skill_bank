from datetime import timedelta
from pathlib import Path

import jwt
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .admin import CallLogAdmin
from .models import (
    CallAuditLog,
    CallLog,
    CallRoom,
    PlatformCallSettings,
    RoleCallPermission,
    UserCallPermission,
)
from .services import get_effective_call_permissions, record_call_audit


class PhaseACallingTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='call_admin',
            email='call_admin@example.com',
            password='AdminPassword123!',
        )
        self.alice = User.objects.create_user(
            username='alice_call',
            email='alice@example.com',
            password='UserPassword123!',
        )
        self.bob = User.objects.create_user(
            username='bob_call',
            email='bob@example.com',
            password='UserPassword123!',
        )

    def test_no_jitsi_references_in_active_code(self):
        base = Path(settings.BASE_DIR)
        files_to_scan = [
            base / 'bookings' / 'models.py',
            base / 'bookings' / 'views.py',
            base / 'bookings' / 'templates' / 'bookings' / 'live_room.html',
            base / 'bookings' / 'templates' / 'bookings' / 'live_sessions.html',
            base / 'bookings' / 'templates' / 'bookings' / 'create_batch.html',
            base / 'bookings' / 'templates' / 'bookings' / 'create_booking.html',
            base / 'user_dashboard' / 'templates' / 'user_dashboard' / 'live_session.html',
        ]
        for path in files_to_scan:
            content = path.read_text(encoding='utf-8').lower()
            self.assertNotIn('jit.si', content, f'Found jit.si in {path}')
            self.assertNotIn('jitsi', content, f'Found jitsi in {path}')

    def test_singleton_platform_settings_and_permissions(self):
        cfg = PlatformCallSettings.get_solo()
        self.assertTrue(cfg.calling_enabled)
        self.assertEqual(cfg.max_participants, 10)

        perms = get_effective_call_permissions(self.alice)
        self.assertTrue(perms['can_call'])
        self.assertTrue(perms['can_screen_share'])

        # Block user -> calling denied on server
        UserCallPermission.objects.create(
            user=self.alice,
            is_blocked_from_calling=True,
            block_reason='Abuse report',
            updated_by=self.admin_user,
        )
        blocked_perms = get_effective_call_permissions(self.alice)
        self.assertFalse(blocked_perms['can_call'])
        self.assertFalse(blocked_perms['can_host'])
        self.assertTrue(blocked_perms['is_blocked'])

        # Global disable overrides role/user permissions
        UserCallPermission.objects.filter(user=self.alice).update(is_blocked_from_calling=False)
        cfg.calling_enabled = False
        cfg.save()
        disabled_perms = get_effective_call_permissions(self.alice)
        self.assertFalse(disabled_perms['can_call'])

    def test_call_log_duration_and_csv_export(self):
        room = CallRoom.objects.create(
            room_code='sv-test-room',
            title='Phase A Test Call',
            host=self.alice,
        )
        now = timezone.now()
        log = CallLog.objects.create(
            room=room,
            caller=self.alice,
            receiver=self.bob,
            call_type='video',
            status='active',
            answered_at=now - timedelta(seconds=95),
        )
        log.finalize('completed', ended_at=now)
        log.refresh_from_db()
        self.assertEqual(log.duration_seconds, 95)
        self.assertEqual(log.status, 'completed')

        factory = RequestFactory()
        request = factory.get('/django-admin/calling/calllog/')
        request.user = self.admin_user
        log_admin = CallLogAdmin(CallLog, admin.site)
        response = log_admin.export_call_logs_csv(request, CallLog.objects.all())
        self.assertEqual(response.status_code, 200)
        csv_text = response.content.decode('utf-8')
        self.assertIn('alice_call', csv_text)
        self.assertIn('bob_call', csv_text)
        self.assertIn('sv-test-room', csv_text)

    def test_admin_registrations_and_audit_log(self):
        for model in (
            PlatformCallSettings,
            RoleCallPermission,
            UserCallPermission,
            CallRoom,
            CallLog,
            CallAuditLog,
        ):
            self.assertIn(model, admin.site._registry)

        entry = record_call_audit(
            self.admin_user,
            'Smoke test action',
            target_user=self.bob,
            target_room_code='sv-test-room',
        )
        self.assertEqual(entry.target_user, self.bob)
        self.assertEqual(CallAuditLog.objects.count(), 1)

    def test_calling_jwt_and_permissions_endpoints(self):
        client = APIClient()
        # Unauthenticated requests must be rejected
        unauth = client.get('/api/v1/calling/token/')
        self.assertIn(unauth.status_code, (401, 403))

        # Session-authenticated user receives SimpleJWT signed with settings.SECRET_KEY
        client.force_authenticate(user=self.alice)
        token_res = client.get('/api/v1/calling/token/')
        self.assertEqual(token_res.status_code, 200)
        body = token_res.json()
        self.assertIn('token', body)
        self.assertEqual(body['user']['username'], 'alice_call')
        self.assertTrue(body['permissions']['can_call'])

        decoded = jwt.decode(body['token'], settings.SECRET_KEY, algorithms=['HS256'])
        self.assertEqual(decoded['user_id'], self.alice.id)
        self.assertEqual(decoded['token_type'], 'access')
        self.assertEqual(decoded['username'], 'alice_call')

        # Permissions endpoint accepts the issued SimpleJWT Bearer token directly
        jwt_client = APIClient()
        jwt_client.credentials(HTTP_AUTHORIZATION=f"Bearer {body['token']}")
        perm_res = jwt_client.get('/api/v1/calling/permissions/')
        self.assertEqual(perm_res.status_code, 200)
        self.assertTrue(perm_res.json()['permissions']['can_call'])

        # Blocking user is immediately reflected via /api/v1/calling/permissions/
        UserCallPermission.objects.create(
            user=self.alice,
            is_blocked_from_calling=True,
            block_reason='Suspended from calling',
        )
        blocked_res = jwt_client.get('/api/v1/calling/permissions/')
        self.assertEqual(blocked_res.status_code, 200)
        self.assertFalse(blocked_res.json()['permissions']['can_call'])
        self.assertTrue(blocked_res.json()['permissions']['is_blocked'])

        # Internal settings endpoint accepts X-Internal-Secret header
        anon_client = APIClient()
        settings_res = anon_client.get(
            '/api/v1/calling/settings/',
            HTTP_X_INTERNAL_SECRET=settings.INTERNAL_CALLING_SECRET,
        )
        self.assertEqual(settings_res.status_code, 200)
        self.assertEqual(settings_res.json()['settings']['max_participants'], 10)

