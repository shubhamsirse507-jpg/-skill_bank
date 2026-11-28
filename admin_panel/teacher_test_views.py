"""
admin_panel/teacher_test_views.py
Unauthenticated (invite-token + session-bound) Teacher Qualification Exam views.
Covers Phase 3 (Test Environment) and Phase 4 (Proctoring Event Ingestion).
"""
import base64
import json
import logging
import secrets
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from notifications.models import Notification

from .ai_generator import draw_questions_for_skill
from .email_helpers import send_brevo_email
from .models import (
    AuditLog,
    InviteAuditLog,
    TeacherMockTest,
    TeacherTestInvite,
    TestViolation,
)

logger = logging.getLogger(__name__)


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _is_rate_limited(key: str, limit: int, window_seconds: int) -> bool:
    """Simple cache-backed sliding/fixed counter rate limiter."""
    count = cache.get(key, 0)
    if count >= limit:
        return True
    if count == 0:
        cache.set(key, 1, timeout=window_seconds)
    else:
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, count + 1, timeout=window_seconds)
    return False


def _grade_mock_test(invite: TeacherTestInvite):
    """Grade mock_test on the server and transition invite + mock_test to SUBMITTED / TAKEN."""
    mock_test = invite.test
    if not mock_test:
        return
    questions = mock_test.questions_json or []
    answers = mock_test.answers_json or {}
    correct_count = 0
    for q in questions:
        q_id = str(q.get('id', ''))
        if answers.get(q_id) == q.get('correct'):
            correct_count += 1

    total = len(questions)
    pct = (correct_count / total) * 100.0 if total > 0 else 0.0
    mock_test.score = correct_count
    mock_test.total_questions = total
    mock_test.percentage = round(pct, 2)
    mock_test.status = 'TAKEN'
    mock_test.save(update_fields=['score', 'total_questions', 'percentage', 'status'])

    invite.status = 'SUBMITTED'
    invite.submitted_at = timezone.now()
    invite.save(update_fields=['status', 'submitted_at', 'updated_at'])


def _require_owning_session(request, invite: TeacherTestInvite) -> bool:
    return request.session.get('teacher_invite_id') == invite.id


def teacher_test_entry(request, token):
    """
    GET /teacher-test/<token>/ : Show sign-in form (test_code + password) or terminal status page.
    POST /teacher-test/<token>/ : Verify test_code + password with constant-time comparison.
    """
    invite = get_object_or_404(
        TeacherTestInvite.objects.select_related('skill', 'test', 'created_by'),
        token=token,
    )

    # Auto-expire INVITED invites past expires_at
    if invite.status == 'INVITED' and invite.is_expired:
        invite.status = 'EXPIRED'
        invite.save(update_fields=['status', 'updated_at'])

    if invite.status in ('EXPIRED', 'REVOKED', 'LOCKED'):
        return render(request, 'admin_panel/teacher_test_status.html', {
            'invite': invite,
            'status_reason': invite.status,
        }, status=403)

    if invite.status in ('SUBMITTED', 'APPROVED', 'REJECTED'):
        review_items = []
        if invite.show_review_to_teacher and invite.status in ('APPROVED', 'REJECTED') and invite.test:
            answers = invite.test.answers_json or {}
            for q in (invite.test.questions_json or []):
                q_id = str(q.get('id', ''))
                review_items.append({
                    'question': q.get('question', ''),
                    'options': q.get('options', {}),
                    'correct': q.get('correct', ''),
                    'user_answer': answers.get(q_id, ''),
                    'explanation': q.get('explanation', ''),
                })
        return render(request, 'admin_panel/teacher_test_status.html', {
            'invite': invite,
            'status_reason': invite.status,
            'review_items': review_items,
        })

    # If already authenticated in session for THIS invite, route appropriately
    if _require_owning_session(request, invite) and request.method == 'GET':
        if invite.status == 'STARTED':
            if invite.is_past_deadline:
                with transaction.atomic():
                    inv_locked = TeacherTestInvite.objects.select_for_update().get(pk=invite.pk)
                    if inv_locked.status == 'STARTED':
                        _grade_mock_test(inv_locked)
                        InviteAuditLog.objects.create(action='test_submitted', invite=inv_locked, notes='Auto-submitted after deadline')
                return redirect('teacher_test_entry', token=token)
            return redirect('teacher_test_exam', token=token)
        return redirect('teacher_test_instructions', token=token)

    error_msg = None
    if request.method == 'POST':
        ip = _client_ip(request)
        if _is_rate_limited(f"tt_signin_ip:{ip}", 20, 600) or _is_rate_limited(f"tt_signin_inv:{invite.id}", 15, 600):
            error_msg = "Too many sign-in attempts. Please wait a few minutes and try again."
            return render(request, 'admin_panel/teacher_test_signin.html', {
                'invite': invite,
                'error_msg': error_msg,
            }, status=429)

        test_code = request.POST.get('test_code', '').strip().upper()
        password = request.POST.get('password', '')

        code_ok = secrets.compare_digest(test_code, invite.test_code.upper())
        pw_ok = invite.check_password(password)

        if code_ok and pw_ok:
            if invite.failed_attempts != 0:
                invite.failed_attempts = 0
                invite.save(update_fields=['failed_attempts', 'updated_at'])
            request.session['teacher_invite_id'] = invite.id
            if invite.status == 'STARTED':
                return redirect('teacher_test_exam', token=token)
            return redirect('teacher_test_instructions', token=token)

        # Failed login attempt
        invite.failed_attempts += 1
        if invite.failed_attempts >= 5:
            invite.status = 'LOCKED'
            invite.save(update_fields=['failed_attempts', 'status', 'updated_at'])
            InviteAuditLog.objects.create(
                action='invite_locked',
                invite=invite,
                notes=f"Locked after {invite.failed_attempts} failed attempts from IP {ip}",
            )
            AuditLog.objects.create(
                admin=invite.created_by,
                action=f"Invite {invite.test_code} ({invite.teacher_email}) LOCKED after 5 failed attempts.",
                target_table='teacher_test_invites',
                target_id=invite.id,
            )
            if invite.created_by:
                Notification.objects.create(
                    user=invite.created_by,
                    title=f"Invite {invite.test_code} Locked",
                    message=f"Teacher invite for {invite.teacher_email} was locked after 5 failed sign-in attempts.",
                    type='system',
                    action_url=f"/admin-panel/hiring/{invite.id}/review/",
                    action_text='Inspect',
                )
                if invite.created_by.email:
                    send_brevo_email(
                        invite.created_by.email,
                        invite.created_by.username,
                        f"Alert: Teacher Invite {invite.test_code} Locked",
                        f"<p>Invite <strong>{invite.test_code}</strong> for {invite.teacher_email} was locked after 5 failed login attempts.</p>",
                        f"Invite {invite.test_code} for {invite.teacher_email} was locked after 5 failed login attempts.",
                    )
            return render(request, 'admin_panel/teacher_test_status.html', {
                'invite': invite,
                'status_reason': 'LOCKED',
            }, status=403)
        else:
            invite.save(update_fields=['failed_attempts', 'updated_at'])
            error_msg = "Invalid test code or password."

    return render(request, 'admin_panel/teacher_test_signin.html', {
        'invite': invite,
        'error_msg': error_msg,
    })


@require_GET
def teacher_test_instructions(request, token):
    """Instructions, privacy notice, consent checkbox, and MediaPipe camera check before Start."""
    invite = get_object_or_404(TeacherTestInvite.objects.select_related('skill'), token=token)
    if not _require_owning_session(request, invite):
        return redirect('teacher_test_entry', token=token)

    if invite.status == 'STARTED':
        return redirect('teacher_test_exam', token=token)
    if invite.status != 'INVITED' or invite.is_expired:
        return redirect('teacher_test_entry', token=token)

    return render(request, 'admin_panel/teacher_test_instructions.html', {
        'invite': invite,
        'snapshots_enabled': getattr(settings, 'PROCTOR_SNAPSHOTS_ENABLED', False),
        'retention_days': getattr(settings, 'PROCTOR_RETENTION_DAYS', 14),
        'allow_no_camera': getattr(settings, 'PROCTOR_ALLOW_NO_CAMERA', False),
        'privacy_note': getattr(settings, 'PROCTOR_PRIVACY_NOTE', ''),
    })


@require_POST
def teacher_test_start(request, token):
    """
    Start the exam inside a transaction with select_for_update.
    Refreshing or re-entering NEVER restarts an already STARTED test.
    """
    invite = get_object_or_404(TeacherTestInvite.objects.select_related('skill'), token=token)
    if not _require_owning_session(request, invite):
        return redirect('teacher_test_entry', token=token)

    consent = request.POST.get('consent') == 'on'
    camera_status = request.POST.get('camera_status', 'verified')

    with transaction.atomic():
        inv = TeacherTestInvite.objects.select_for_update().select_related('skill').get(pk=invite.pk)

        if inv.status == 'STARTED':
            return redirect('teacher_test_exam', token=token)
        if inv.status != 'INVITED' or inv.is_expired:
            return redirect('teacher_test_entry', token=token)

        if not consent:
            messages.error(request, "You must accept the exam rules and monitoring consent to begin.")
            return redirect('teacher_test_instructions', token=token)

        allow_no_cam = getattr(settings, 'PROCTOR_ALLOW_NO_CAMERA', False)
        proctoring_skipped = False
        if camera_status == 'skipped':
            if not allow_no_cam:
                messages.error(request, "Camera verification is required before starting this exam.")
                return redirect('teacher_test_instructions', token=token)
            proctoring_skipped = True

        questions = draw_questions_for_skill(
            skill=inv.skill,
            skill_name=inv.skill.title,
            count=inv.question_count,
            skill_level=inv.skill_level,
        )
        from django.contrib.auth.models import User
        matched_user = User.objects.filter(email__iexact=inv.teacher_email).first()

        mock_test = TeacherMockTest.objects.create(
            teacher=matched_user,
            skill=inv.skill,
            skill_name=inv.skill.title[:150],
            skill_level=inv.skill_level,
            questions_json=questions,
            answers_json={},
            total_questions=len(questions),
            status='PENDING',
        )

        inv.started_at = timezone.now()
        inv.status = 'STARTED'
        inv.test = mock_test
        inv.proctoring_skipped = proctoring_skipped
        inv.save(update_fields=['started_at', 'status', 'test', 'proctoring_skipped', 'updated_at'])

        InviteAuditLog.objects.create(
            action='test_started',
            invite=inv,
            notes='Proctoring skipped (no camera)' if proctoring_skipped else 'Camera verified',
        )

    return redirect('teacher_test_exam', token=token)


@require_GET
def teacher_test_exam(request, token):
    """
    Live exam page: serves 1 question at a time via fetch, countdown from server time,
    and runs browser-only MediaPipe proctoring + tab/fullscreen deterrents.
    NEVER sends correct answers or explanations to the browser.
    """
    invite = get_object_or_404(TeacherTestInvite.objects.select_related('skill', 'test'), token=token)
    if not _require_owning_session(request, invite):
        return redirect('teacher_test_entry', token=token)

    if invite.status != 'STARTED' or not invite.test:
        return redirect('teacher_test_entry', token=token)

    if invite.is_past_deadline:
        with transaction.atomic():
            inv = TeacherTestInvite.objects.select_for_update().get(pk=invite.pk)
            if inv.status == 'STARTED':
                _grade_mock_test(inv)
                InviteAuditLog.objects.create(action='test_submitted', invite=inv, notes='Auto-submitted at deadline')
        return redirect('teacher_test_entry', token=token)

    remaining_seconds = max(0, int((invite.deadline - timezone.now()).total_seconds()))
    total_questions = len(invite.test.questions_json or [])
    saved_keys = list((invite.test.answers_json or {}).keys())

    return render(request, 'admin_panel/teacher_test_exam.html', {
        'invite': invite,
        'total_questions': total_questions,
        'remaining_seconds': remaining_seconds,
        'saved_keys_json': json.dumps(saved_keys),
        'snapshots_enabled': getattr(settings, 'PROCTOR_SNAPSHOTS_ENABLED', False),
        'auto_submit_threshold': getattr(settings, 'PROCTOR_AUTO_SUBMIT_THRESHOLD', 0),
    })


@require_GET
def teacher_test_question(request, token, idx):
    """Return a single question WITHOUT correct answer or explanation."""
    invite = get_object_or_404(TeacherTestInvite.objects.select_related('test'), token=token)
    if not _require_owning_session(request, invite):
        return JsonResponse({'error': 'Unauthorized session'}, status=403)
    if invite.status != 'STARTED' or not invite.test:
        return JsonResponse({'error': 'Exam is not active'}, status=400)
    if invite.is_past_deadline:
        return JsonResponse({'error': 'Time limit exceeded'}, status=403)

    questions = invite.test.questions_json or []
    if idx < 1 or idx > len(questions):
        return JsonResponse({'error': 'Question index out of range'}, status=404)

    q = questions[idx - 1]
    q_id = str(q.get('id', idx))
    saved_answer = (invite.test.answers_json or {}).get(q_id, '')
    remaining_seconds = max(0, int((invite.deadline - timezone.now()).total_seconds()))

    return JsonResponse({
        'idx': idx,
        'total': len(questions),
        'question_id': q_id,
        'question': q.get('question', ''),
        'options': q.get('options', {}),
        'saved_answer': saved_answer,
        'remaining_seconds': remaining_seconds,
    })


@require_POST
def teacher_test_answer(request, token):
    """Save a single answer for the owning session's active exam."""
    invite = get_object_or_404(TeacherTestInvite, token=token)
    if not _require_owning_session(request, invite):
        return JsonResponse({'error': 'Unauthorized session'}, status=403)
    if invite.status != 'STARTED':
        return JsonResponse({'error': 'Exam is not active'}, status=400)
    if invite.is_past_deadline:
        return JsonResponse({'error': 'Deadline exceeded; answers are no longer accepted.'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        payload = request.POST

    q_id = str(payload.get('question_id', '')).strip()
    option = str(payload.get('option', '')).strip().upper()
    if option not in ('A', 'B', 'C', 'D'):
        return JsonResponse({'error': 'Invalid option'}, status=400)

    with transaction.atomic():
        inv = TeacherTestInvite.objects.select_for_update().select_related('test').get(pk=invite.pk)
        if inv.status != 'STARTED' or inv.is_past_deadline or not inv.test:
            return JsonResponse({'error': 'Cannot save answer'}, status=403)
        answers = dict(inv.test.answers_json or {})
        answers[q_id] = option
        inv.test.answers_json = answers
        inv.test.save(update_fields=['answers_json'])

    return JsonResponse({'ok': True, 'saved_count': len(answers)})


@require_POST
def teacher_test_submit(request, token):
    """Submit and grade the active exam on the server (one attempt only)."""
    invite = get_object_or_404(TeacherTestInvite, token=token)
    if not _require_owning_session(request, invite):
        return JsonResponse({'error': 'Unauthorized session'}, status=403) if request.headers.get('Accept') == 'application/json' else redirect('teacher_test_entry', token=token)

    with transaction.atomic():
        inv = TeacherTestInvite.objects.select_for_update().select_related('test').get(pk=invite.pk)
        if inv.status != 'STARTED':
            return redirect('teacher_test_entry', token=token)

        was_late = inv.is_past_deadline
        _grade_mock_test(inv)
        InviteAuditLog.objects.create(
            action='test_submitted',
            invite=inv,
            notes='Submitted (auto-graded after deadline)' if was_late else 'Submitted by candidate',
        )

    return redirect('teacher_test_entry', token=token)


@require_POST
def teacher_test_proctor_event(request, token):
    """
    Record a proctoring or deterrent event for the owning session's STARTED invite.
    Optionally stores a small JPEG snapshot in PRIVATE_MEDIA_ROOT if PROCTOR_SNAPSHOTS_ENABLED=True.
    """
    invite = get_object_or_404(TeacherTestInvite, token=token)
    if not _require_owning_session(request, invite):
        return JsonResponse({'error': 'Unauthorized session'}, status=403)
    if invite.status != 'STARTED':
        return JsonResponse({'error': 'Events accepted only while test is STARTED'}, status=400)

    ip = _client_ip(request)
    if _is_rate_limited(f"proctor_evt:{invite.id}:{ip}", 60, 60):
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    evt_type = str(payload.get('type', '')).strip()
    valid_types = {c[0] for c in TestViolation.TYPE_CHOICES}
    if evt_type not in valid_types:
        return JsonResponse({'error': 'Invalid violation type'}, status=400)

    try:
        duration = max(0.0, min(3600.0, float(payload.get('duration_seconds', 0.0))))
    except (ValueError, TypeError):
        duration = 0.0

    snapshot_rel = ''
    snapshot_b64 = payload.get('snapshot_jpeg', '')
    if getattr(settings, 'PROCTOR_SNAPSHOTS_ENABLED', False) and isinstance(snapshot_b64, str) and snapshot_b64:
        try:
            if ',' in snapshot_b64:
                snapshot_b64 = snapshot_b64.split(',', 1)[1]
            raw_bytes = base64.b64decode(snapshot_b64, validate=True)
            if 0 < len(raw_bytes) <= 250_000:
                private_root = Path(getattr(settings, 'PRIVATE_MEDIA_ROOT', settings.BASE_DIR / 'private_media')).resolve()
                sub_dir = private_root / f"invite_{invite.id}"
                sub_dir.mkdir(parents=True, exist_ok=True)
                fname = f"{uuid.uuid4().hex}.jpg"
                (sub_dir / fname).write_bytes(raw_bytes)
                snapshot_rel = f"invite_{invite.id}/{fname}"
        except Exception as exc:
            logger.warning("[Proctor] Snapshot save skipped: %s", exc)

    with transaction.atomic():
        inv = TeacherTestInvite.objects.select_for_update().select_related('test').get(pk=invite.pk)
        if inv.status != 'STARTED':
            return JsonResponse({'error': 'Exam no longer active'}, status=400)

        TestViolation.objects.create(
            invite=inv,
            type=evt_type,
            duration_seconds=duration,
            snapshot_path=snapshot_rel,
        )
        inv.violation_count += 1
        inv.save(update_fields=['violation_count', 'updated_at'])

        threshold = int(getattr(settings, 'PROCTOR_AUTO_SUBMIT_THRESHOLD', 0) or 0)
        auto_submitted = False
        if threshold > 0 and inv.violation_count >= threshold:
            _grade_mock_test(inv)
            InviteAuditLog.objects.create(
                action='test_submitted',
                invite=inv,
                notes=f'Auto-submitted at proctor threshold ({threshold} events)',
            )
            auto_submitted = True

    return JsonResponse({
        'ok': True,
        'violation_count': inv.violation_count,
        'auto_submitted': auto_submitted,
    })
