"""
admin_panel/tests.py
Comprehensive test suite for the secure, invite-based Teacher Qualification & Hiring system.
"""
import base64
import datetime
import json
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

# ---------------------------------------------------------------------------
# Python 3.14 compatibility fix for Django's Context.__copy__
#
# Python 3.14 changed how super().__copy__() works: it now returns a 'super'
# proxy object instead of a shallow copy of self, breaking Django's
# BaseContext.__copy__ and RequestContext.__copy__.  This monkey-patch replaces
# both methods with an implementation that works on 3.11–3.14.
# ---------------------------------------------------------------------------
def _patched_base_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.__dict__.update(self.__dict__)
    duplicate.dicts = self.dicts[:]
    return duplicate

try:
    from django.template.context import BaseContext, RequestContext

    def _patched_request_context_copy(self):
        duplicate = _patched_base_context_copy(self)
        return duplicate

    BaseContext.__copy__ = _patched_base_context_copy
    RequestContext.__copy__ = _patched_request_context_copy
except Exception:
    pass  # If Django changes internals, don't break imports
# ---------------------------------------------------------------------------

from notifications.models import Notification
from skill_management.models import Skill, SkillCategory

from .ai_generator import draw_questions_for_skill
from .models import (
    AuditLog,
    InviteAuditLog,
    QuestionBank,
    TeacherMockTest,
    TeacherTestInvite,
    TestViolation,
    VerifiedTeacherSkill,
)


class TeacherHiringFlowTests(TestCase):
    def setUp(self):
        call_command('seed_question_bank')
        self.admin = User.objects.create_user(
            username='admin1', email='admin1@example.com', password='AdminPass123!', is_staff=True
        )
        self.teacher_user = User.objects.create_user(
            username='teacher1', email='teacher1@example.com', password='UserPass123!'
        )
        self.other_user = User.objects.create_user(
            username='other1', email='other1@example.com', password='UserPass123!'
        )
        self.cat_tech = SkillCategory.objects.create(category_name='Technology')
        self.cat_music = SkillCategory.objects.create(category_name='Music')

        self.python_skill = Skill.objects.create(
            user=self.admin, category=self.cat_tech, title='Python & Django', status='approved'
        )
        self.guitar_skill = Skill.objects.create(
            user=self.admin, category=self.cat_music, title='Acoustic Guitar', status='approved'
        )

    def _create_invite(self, email='teacher1@example.com', skill=None, expires_delta_days=3, pass_mark=60, time_limit=20):
        skill = skill or self.python_skill
        return TeacherTestInvite.create_invite(
            teacher_email=email,
            teacher_name='Teacher One',
            skill=skill,
            skill_level='Intermediate',
            pass_mark=pass_mark,
            time_limit_minutes=time_limit,
            question_count=5,
            expires_at=timezone.now() + datetime.timedelta(days=expires_delta_days),
            created_by=self.admin,
        )

    def _sign_in_invite(self, client, invite, raw_pw):
        url = reverse('teacher_test_entry', kwargs={'token': invite.token})
        return client.post(url, {'test_code': invite.test_code, 'password': raw_pw})

    def test_whole_word_question_matching_guitar_not_ui(self):
        """'ui' in 'Acoustic Guitar' must NOT pick UI/UX design questions."""
        qs = draw_questions_for_skill(skill=self.guitar_skill, count=5)
        self.assertEqual(len(qs), 5)
        joined = ' '.join(q['question'].lower() for q in qs)
        self.assertNotIn('wireframe', joined)
        self.assertNotIn('wcag', joined)

    def test_get_entry_creates_no_db_rows(self):
        """GET on teacher test entry or admin hiring must never create TeacherMockTest rows."""
        invite, _ = self._create_invite()
        before_tests = TeacherMockTest.objects.count()
        before_invites = TeacherTestInvite.objects.count()

        c = Client()
        resp = c.get(reverse('teacher_test_entry', kwargs={'token': invite.token}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(TeacherMockTest.objects.count(), before_tests)
        self.assertEqual(TeacherTestInvite.objects.count(), before_invites)

        self.client.force_login(self.admin)
        resp2 = self.client.get(reverse('admin_panel:hiring'))
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(TeacherMockTest.objects.count(), before_tests)

    def test_wrong_password_lockout_after_5_attempts(self):
        invite, _ = self._create_invite()
        c = Client()
        url = reverse('teacher_test_entry', kwargs={'token': invite.token})

        for i in range(4):
            resp = c.post(url, {'test_code': invite.test_code, 'password': 'wrong'})
            self.assertEqual(resp.status_code, 200)
            invite.refresh_from_db()
            self.assertEqual(invite.failed_attempts, i + 1)
            self.assertEqual(invite.status, 'INVITED')

        # 5th attempt locks
        resp5 = c.post(url, {'test_code': invite.test_code, 'password': 'wrong'})
        self.assertEqual(resp5.status_code, 403)
        invite.refresh_from_db()
        self.assertEqual(invite.status, 'LOCKED')
        self.assertTrue(Notification.objects.filter(user=self.admin).exists())

    def test_expired_revoked_and_reused_links_rejected(self):
        # Expired
        inv_exp, pw_exp = self._create_invite(expires_delta_days=-1)
        c = Client()
        r1 = c.get(reverse('teacher_test_entry', kwargs={'token': inv_exp.token}))
        self.assertEqual(r1.status_code, 403)
        inv_exp.refresh_from_db()
        self.assertEqual(inv_exp.status, 'EXPIRED')

        # Revoked
        inv_rev, pw_rev = self._create_invite()
        inv_rev.status = 'REVOKED'
        inv_rev.save()
        r2 = self._sign_in_invite(c, inv_rev, pw_rev)
        self.assertEqual(r2.status_code, 403)

        # Reused after submit
        inv_sub, pw_sub = self._create_invite()
        self._sign_in_invite(c, inv_sub, pw_sub)
        c.post(reverse('teacher_test_start', kwargs={'token': inv_sub.token}), {'consent': 'on', 'camera_status': 'verified'})
        c.post(reverse('teacher_test_submit', kwargs={'token': inv_sub.token}))
        inv_sub.refresh_from_db()
        self.assertEqual(inv_sub.status, 'SUBMITTED')
        # Trying to start again must not restart
        c.post(reverse('teacher_test_start', kwargs={'token': inv_sub.token}), {'consent': 'on', 'camera_status': 'verified'})
        inv_sub.refresh_from_db()
        self.assertEqual(inv_sub.status, 'SUBMITTED')

    def test_starting_twice_does_not_restart_timer(self):
        invite, raw_pw = self._create_invite()
        c = Client()
        self._sign_in_invite(c, invite, raw_pw)

        c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})
        invite.refresh_from_db()
        first_started_at = invite.started_at
        first_test_id = invite.test_id
        self.assertEqual(invite.status, 'STARTED')
        self.assertIsNotNone(first_started_at)

        # Second start attempt
        c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})
        invite.refresh_from_db()
        self.assertEqual(invite.started_at, first_started_at)
        self.assertEqual(invite.test_id, first_test_id)

    def test_answers_rejected_after_deadline(self):
        invite, raw_pw = self._create_invite(time_limit=10)
        c = Client()
        self._sign_in_invite(c, invite, raw_pw)
        c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})

        # Force started_at far into the past (> time_limit + 10s grace)
        invite.refresh_from_db()
        invite.started_at = timezone.now() - datetime.timedelta(minutes=15)
        invite.save(update_fields=['started_at'])

        resp = c.post(
            reverse('teacher_test_answer', kwargs={'token': invite.token}),
            data=json.dumps({'question_id': '1', 'option': 'A'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_correct_answers_absent_from_page_and_question_api(self):
        invite, raw_pw = self._create_invite()
        c = Client()
        self._sign_in_invite(c, invite, raw_pw)
        c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})

        exam_resp = c.get(reverse('teacher_test_exam', kwargs={'token': invite.token}))
        self.assertEqual(exam_resp.status_code, 200)
        body = exam_resp.content.decode('utf-8')
        self.assertNotIn('"correct"', body)
        self.assertNotIn('"explanation"', body)

        q_resp = c.get(reverse('teacher_test_question', kwargs={'token': invite.token, 'idx': 1}))
        self.assertEqual(q_resp.status_code, 200)
        q_data = q_resp.json()
        self.assertNotIn('correct', q_data)
        self.assertNotIn('explanation', q_data)

    def test_other_session_cannot_submit_or_post_events(self):
        invite, raw_pw = self._create_invite()
        c_owner = Client()
        self._sign_in_invite(c_owner, invite, raw_pw)
        c_owner.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})

        # Attacker with a different session
        c_attacker = Client()
        r_ans = c_attacker.post(
            reverse('teacher_test_answer', kwargs={'token': invite.token}),
            data=json.dumps({'question_id': '1', 'option': 'A'}),
            content_type='application/json',
        )
        self.assertEqual(r_ans.status_code, 403)

        r_sub = c_attacker.post(reverse('teacher_test_submit', kwargs={'token': invite.token}))
        invite.refresh_from_db()
        self.assertEqual(invite.status, 'STARTED')  # still STARTED, not submitted

        r_evt = c_attacker.post(
            reverse('teacher_test_proctor_event', kwargs={'token': invite.token}),
            data=json.dumps({'type': 'tab_switch', 'duration_seconds': 2.0}),
            content_type='application/json',
        )
        self.assertEqual(r_evt.status_code, 403)

    def test_proctor_events_accepted_only_while_started(self):
        invite, raw_pw = self._create_invite()
        c = Client()
        self._sign_in_invite(c, invite, raw_pw)

        # Before STARTED (INVITED) -> rejected
        r_before = c.post(
            reverse('teacher_test_proctor_event', kwargs={'token': invite.token}),
            data=json.dumps({'type': 'tab_switch', 'duration_seconds': 1.5}),
            content_type='application/json',
        )
        self.assertEqual(r_before.status_code, 400)

        # Start -> accepted
        c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})
        r_during = c.post(
            reverse('teacher_test_proctor_event', kwargs={'token': invite.token}),
            data=json.dumps({'type': 'tab_switch', 'duration_seconds': 1.5}),
            content_type='application/json',
        )
        self.assertEqual(r_during.status_code, 200)
        invite.refresh_from_db()
        self.assertEqual(invite.violation_count, 1)

        # Submit -> rejected again
        c.post(reverse('teacher_test_submit', kwargs={'token': invite.token}))
        r_after = c.post(
            reverse('teacher_test_proctor_event', kwargs={'token': invite.token}),
            data=json.dumps({'type': 'tab_switch', 'duration_seconds': 1.5}),
            content_type='application/json',
        )
        self.assertEqual(r_after.status_code, 400)

    def test_admin_cannot_decide_non_submitted_invite(self):
        invite, _ = self._create_invite()
        self.client.force_login(self.admin)

        self.client.post(
            reverse('admin_panel:decide_invite', kwargs={'invite_id': invite.id}),
            {'action': 'approve', 'admin_notes': 'Trying early'},
        )
        invite.refresh_from_db()
        self.assertEqual(invite.status, 'INVITED')
        self.assertFalse(VerifiedTeacherSkill.objects.filter(test=invite).exists())

    def test_approve_creates_verified_skill_audit_and_notification(self):
        invite, raw_pw = self._create_invite(email=self.teacher_user.email, pass_mark=0)
        c = Client()
        self._sign_in_invite(c, invite, raw_pw)
        c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})
        c.post(reverse('teacher_test_submit', kwargs={'token': invite.token}))

        self.client.force_login(self.admin)
        self.client.post(
            reverse('admin_panel:decide_invite', kwargs={'invite_id': invite.id}),
            {'action': 'approve', 'admin_notes': 'Great answers'},
        )
        invite.refresh_from_db()
        self.assertEqual(invite.status, 'APPROVED')
        self.assertTrue(
            VerifiedTeacherSkill.objects.filter(
                user=self.teacher_user, skill=self.python_skill, is_active=True
            ).exists()
        )
        self.assertTrue(AuditLog.objects.filter(target_table='teacher_test_invites', target_id=invite.id).exists())
        self.assertTrue(InviteAuditLog.objects.filter(invite=invite, action='test_approved').exists())
        self.assertTrue(Notification.objects.filter(user=self.teacher_user, type='achievement').exists())

    def test_snapshots_private_and_retention_cleanup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(PRIVATE_MEDIA_ROOT=Path(tmpdir), PROCTOR_SNAPSHOTS_ENABLED=True, PROCTOR_RETENTION_DAYS=7):
                invite, raw_pw = self._create_invite()
                c = Client()
                self._sign_in_invite(c, invite, raw_pw)
                c.post(reverse('teacher_test_start', kwargs={'token': invite.token}), {'consent': 'on', 'camera_status': 'verified'})

                fake_jpeg = base64.b64encode(b'\xff\xd8\xff\xe0TESTJPEG').decode('ascii')
                r = c.post(
                    reverse('teacher_test_proctor_event', kwargs={'token': invite.token}),
                    data=json.dumps({'type': 'no_face', 'duration_seconds': 3.5, 'snapshot_jpeg': fake_jpeg}),
                    content_type='application/json',
                )
                self.assertEqual(r.status_code, 200)
                v = TestViolation.objects.get(invite=invite)
                self.assertTrue(bool(v.snapshot_path))
                self.assertTrue((Path(tmpdir) / v.snapshot_path).exists())

                snap_url = reverse('admin_panel:view_proctor_snapshot', kwargs={'violation_id': v.id})
                # Anonymous / non-admin cannot access snapshot
                r_anon = Client().get(snap_url)
                self.assertEqual(r_anon.status_code, 302)
                c_non_admin = Client()
                c_non_admin.force_login(self.other_user)
                r_non = c_non_admin.get(snap_url)
                self.assertEqual(r_non.status_code, 302)

                # Admin CAN access snapshot
                c_admin = Client()
                c_admin.force_login(self.admin)
                r_adm = c_admin.get(snap_url)
                self.assertEqual(r_adm.status_code, 200)
                r_adm.close()

                # Retention cleanup deletes old snapshots
                v.started_at = timezone.now() - datetime.timedelta(days=10)
                v.save(update_fields=['started_at'])
                call_command('cleanup_proctor_snapshots')
                v.refresh_from_db()
                self.assertEqual(v.snapshot_path, '')

    def test_camera_denied_fallback_recorded(self):
        with override_settings(PROCTOR_ALLOW_NO_CAMERA=True):
            invite, raw_pw = self._create_invite()
            c = Client()
            self._sign_in_invite(c, invite, raw_pw)
            c.post(
                reverse('teacher_test_start', kwargs={'token': invite.token}),
                {'consent': 'on', 'camera_status': 'skipped'},
            )
            invite.refresh_from_db()
            self.assertEqual(invite.status, 'STARTED')
            self.assertTrue(invite.proctoring_skipped)


