"""
admin_panel/hiring_views.py
Admin-only views for the invite-based Teacher Qualification & Hiring workflow.
All views enforce @login_required + @user_passes_test(is_admin).
All state changes require POST + CSRF and write AuditLog + InviteAuditLog.
"""
import datetime
import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from notifications.models import Notification
from skill_management.models import Skill

from .email_helpers import send_brevo_email
from .models import (
    AuditLog,
    InviteAuditLog,
    TeacherMockTest,
    TeacherTestInvite,
    TestViolation,
    VerifiedTeacherSkill,
)

logger = logging.getLogger(__name__)


def is_admin(user):
    return user.is_authenticated and (
        user.is_staff or (getattr(user, 'profile', None) and user.profile.role == 'admin')
    )


def _send_invite_emails(request, invite, raw_password):
    """
    Send 2 separate emails via Brevo:
      1) Exam link + test_code + time limit + expiry
      2) Password (separate email for security)
    """
    exam_url = request.build_absolute_uri(
        reverse('teacher_test_entry', kwargs={'token': invite.token})
    )
    name = invite.teacher_name or invite.teacher_email
    expiry_str = invite.expires_at.strftime('%Y-%m-%d %H:%M UTC')

    subj1 = f"Skill-Verse Teacher Exam Invitation — {invite.skill.title}"
    plain1 = (
        f"Hello {name},\n\n"
        f"You have been invited to take the Skill-Verse qualification exam for '{invite.skill.title}' ({invite.skill_level}).\n\n"
        f"Exam Link: {exam_url}\n"
        f"Test Code: {invite.test_code}\n"
        f"Time Limit: {invite.time_limit_minutes} minutes\n"
        f"Expires At: {expiry_str}\n\n"
        f"Your exam password will arrive in a separate email.\n\n"
        f"— Skill-Verse Team"
    )
    html1 = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:560px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;border-radius:12px;">
      <h2 style="color:#0c6c63;margin-top:0;">Skill-Verse Teacher Qualification Exam</h2>
      <p>Hello <strong>{name}</strong>,</p>
      <p>You have been invited to qualify as a verified teacher for <strong>{invite.skill.title}</strong> ({invite.skill_level}).</p>
      <div style="background:#f0fdf9;border:1px solid #99f6e4;border-radius:10px;padding:16px;margin:16px 0;">
        <p style="margin:4px 0;"><strong>Test Code:</strong> <code>{invite.test_code}</code></p>
        <p style="margin:4px 0;"><strong>Time Limit:</strong> {invite.time_limit_minutes} minutes (1 attempt)</p>
        <p style="margin:4px 0;"><strong>Expires:</strong> {expiry_str}</p>
      </div>
      <p style="text-align:center;margin:24px 0;">
        <a href="{exam_url}" style="background:#0c6c63;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700;">Open Exam Portal</a>
      </p>
      <p style="color:#64748b;font-size:13px;">Your exam password is sent in a separate email.</p>
    </div>
    """

    subj2 = f"Your Skill-Verse Exam Password ({invite.test_code})"
    plain2 = (
        f"Hello {name},\n\n"
        f"Here is your password for Skill-Verse Test Code {invite.test_code}:\n\n"
        f"Password: {raw_password}\n\n"
        f"Keep this confidential. Do not share it with anyone.\n"
        f"— Skill-Verse Team"
    )
    html2 = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:560px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;border-radius:12px;">
      <h2 style="color:#0c6c63;margin-top:0;">Exam Access Password</h2>
      <p>Hello <strong>{name}</strong>,</p>
      <p>Use this password with Test Code <strong>{invite.test_code}</strong>:</p>
      <div style="text-align:center;margin:20px 0;">
        <span style="display:inline-block;font-size:22px;font-weight:800;letter-spacing:2px;background:#e8f7f5;color:#0c6c63;padding:10px 22px;border-radius:8px;border:1px dashed #0c6c63;">{raw_password}</span>
      </div>
    </div>
    """

    sent1 = send_brevo_email(invite.teacher_email, name, subj1, html1, plain1)
    sent2 = send_brevo_email(invite.teacher_email, name, subj2, html2, plain2)
    return sent1 and sent2


@login_required
@user_passes_test(is_admin)
def admin_teacher_hiring(request):
    """Admin-only Teacher Hiring dashboard using TeacherTestInvite."""
    invites = (
        TeacherTestInvite.objects
        .select_related('skill', 'test', 'created_by')
        .order_by('-created_at')
    )
    skills = Skill.objects.select_related('category').order_by('title')

    stats = {
        'total': invites.count(),
        'invited': invites.filter(status='INVITED').count(),
        'started': invites.filter(status='STARTED').count(),
        'submitted': invites.filter(status='SUBMITTED').count(),
        'approved': invites.filter(status='APPROVED').count(),
        'rejected': invites.filter(status='REJECTED').count(),
        'locked': invites.filter(status='LOCKED').count(),
    }
    one_time_creds = request.session.pop('last_invite_creds', None)

    return render(request, 'admin_panel/hiring.html', {
        'invites': invites,
        'skills': skills,
        'stats': stats,
        'one_time_creds': one_time_creds,
        'active_tab': 'hiring',
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def create_teacher_invite(request):
    """Create a new TeacherTestInvite, email link + password, and log AuditLog."""
    teacher_email = request.POST.get('teacher_email', '').strip().lower()
    teacher_name = request.POST.get('teacher_name', '').strip()[:200]
    skill_id = request.POST.get('skill_id')
    skill_level = request.POST.get('skill_level', 'Intermediate').strip()[:50]

    try:
        pass_mark = max(1, min(100, int(request.POST.get('pass_mark', 60))))
        time_limit = max(5, min(180, int(request.POST.get('time_limit_minutes', 20))))
        question_count = max(3, min(50, int(request.POST.get('question_count', 10))))
        expiry_days = max(1, min(30, int(request.POST.get('expiry_days', 3))))
    except (ValueError, TypeError):
        messages.error(request, "Invalid numeric parameter for invite.")
        return redirect('admin_panel:hiring')

    if not teacher_email or '@' not in teacher_email or not skill_id:
        messages.error(request, "Valid email and skill are required.")
        return redirect('admin_panel:hiring')

    skill = get_object_or_404(Skill, pk=skill_id)

    # 7-day cooldown after rejection for the same email + skill
    cooldown_cutoff = timezone.now() - datetime.timedelta(days=7)
    recent_rejection = TeacherTestInvite.objects.filter(
        teacher_email__iexact=teacher_email,
        skill=skill,
        status='REJECTED',
        updated_at__gte=cooldown_cutoff,
    ).exists()
    if recent_rejection:
        messages.error(
            request,
            f"{teacher_email} was rejected for '{skill.title}' within the last 7 days. Re-invite is allowed after 7 days."
        )
        return redirect('admin_panel:hiring')

    expires_at = timezone.now() + datetime.timedelta(days=expiry_days)

    with transaction.atomic():
        invite, raw_password = TeacherTestInvite.create_invite(
            teacher_email=teacher_email,
            teacher_name=teacher_name,
            skill=skill,
            skill_level=skill_level,
            pass_mark=pass_mark,
            time_limit_minutes=time_limit,
            question_count=question_count,
            expires_at=expires_at,
            created_by=request.user,
        )
        AuditLog.objects.create(
            admin=request.user,
            action=f"Invited {teacher_email} for skill '{skill.title}' ({invite.test_code}).",
            target_table='teacher_test_invites',
            target_id=invite.id,
        )
        InviteAuditLog.objects.create(
            admin=request.user,
            action='invite_created',
            invite=invite,
            notes=f"Pass mark: {pass_mark}%, Time: {time_limit}m, Questions: {question_count}",
        )

    emails_ok = _send_invite_emails(request, invite, raw_password)
    exam_path = reverse('teacher_test_entry', kwargs={'token': invite.token})
    request.session['last_invite_creds'] = {
        'teacher_email': invite.teacher_email,
        'test_code': invite.test_code,
        'password': raw_password,
        'exam_url': request.build_absolute_uri(exam_path),
        'emails_sent': emails_ok,
    }
    if emails_ok:
        messages.success(request, f"Invite {invite.test_code} created & emailed to {teacher_email}.")
    else:
        messages.warning(
            request,
            f"Invite {invite.test_code} created, but email delivery failed/unconfigured. Copy credentials from the banner below."
        )
    return redirect('admin_panel:hiring')


@login_required
@user_passes_test(is_admin)
@require_POST
def revoke_invite(request, invite_id):
    invite = get_object_or_404(TeacherTestInvite, pk=invite_id)
    if invite.status not in ('INVITED', 'STARTED', 'LOCKED'):
        messages.error(request, f"Cannot revoke invite in status '{invite.status}'.")
        return redirect('admin_panel:hiring')

    with transaction.atomic():
        invite.status = 'REVOKED'
        invite.save(update_fields=['status', 'updated_at'])
        AuditLog.objects.create(
            admin=request.user,
            action=f"Revoked invite {invite.test_code} ({invite.teacher_email}).",
            target_table='teacher_test_invites',
            target_id=invite.id,
        )
        InviteAuditLog.objects.create(
            admin=request.user,
            action='invite_revoked',
            invite=invite,
        )
    messages.warning(request, f"Invite {invite.test_code} revoked.")
    return redirect('admin_panel:hiring')


@login_required
@user_passes_test(is_admin)
@require_POST
def resend_invite(request, invite_id):
    invite = get_object_or_404(TeacherTestInvite, pk=invite_id)
    if invite.status in ('SUBMITTED', 'APPROVED', 'REJECTED'):
        messages.error(request, f"Cannot resend invite in status '{invite.status}'.")
        return redirect('admin_panel:hiring')

    with transaction.atomic():
        raw_password = invite.regenerate_credentials()
        if invite.is_expired:
            invite.expires_at = timezone.now() + datetime.timedelta(days=3)
            invite.save(update_fields=['expires_at'])
        AuditLog.objects.create(
            admin=request.user,
            action=f"Resent invite {invite.test_code} ({invite.teacher_email}) with new token & password.",
            target_table='teacher_test_invites',
            target_id=invite.id,
        )
        InviteAuditLog.objects.create(
            admin=request.user,
            action='invite_resent',
            invite=invite,
        )

    emails_ok = _send_invite_emails(request, invite, raw_password)
    exam_path = reverse('teacher_test_entry', kwargs={'token': invite.token})
    request.session['last_invite_creds'] = {
        'teacher_email': invite.teacher_email,
        'test_code': invite.test_code,
        'password': raw_password,
        'exam_url': request.build_absolute_uri(exam_path),
        'emails_sent': emails_ok,
    }
    messages.success(request, f"Invite {invite.test_code} regenerated & resent to {invite.teacher_email}.")
    return redirect('admin_panel:hiring')


@login_required
@user_passes_test(is_admin)
@require_POST
def extend_invite(request, invite_id):
    invite = get_object_or_404(TeacherTestInvite, pk=invite_id)
    if invite.status in ('SUBMITTED', 'APPROVED', 'REJECTED', 'REVOKED'):
        messages.error(request, f"Cannot extend invite in status '{invite.status}'.")
        return redirect('admin_panel:hiring')

    try:
        days = max(1, min(30, int(request.POST.get('days', 3))))
    except (ValueError, TypeError):
        days = 3

    with transaction.atomic():
        base = max(timezone.now(), invite.expires_at)
        invite.expires_at = base + datetime.timedelta(days=days)
        if invite.status == 'EXPIRED':
            invite.status = 'INVITED'
        invite.save(update_fields=['expires_at', 'status', 'updated_at'])
        AuditLog.objects.create(
            admin=request.user,
            action=f"Extended invite {invite.test_code} by {days} day(s).",
            target_table='teacher_test_invites',
            target_id=invite.id,
        )
        InviteAuditLog.objects.create(
            admin=request.user,
            action='invite_extended',
            invite=invite,
            notes=f"Extended by {days} day(s) until {invite.expires_at.strftime('%Y-%m-%d %H:%M UTC')}",
        )
    messages.success(request, f"Invite {invite.test_code} extended by {days} day(s).")
    return redirect('admin_panel:hiring')


@login_required
@user_passes_test(is_admin)
def review_invite(request, invite_id):
    """Admin review page showing score vs pass mark, time taken, violation timeline, snapshots, audit trail."""
    invite = get_object_or_404(
        TeacherTestInvite.objects.select_related('skill', 'test', 'created_by'),
        pk=invite_id,
    )
    violations = invite.violations.all()
    audit_logs = invite.audit_logs.select_related('admin').all()

    time_taken_seconds = None
    if invite.started_at and invite.submitted_at:
        time_taken_seconds = int((invite.submitted_at - invite.started_at).total_seconds())

    review_items = []
    if invite.test and invite.test.questions_json:
        answers = invite.test.answers_json or {}
        for q in invite.test.questions_json:
            q_id = str(q.get('id', ''))
            user_ans = answers.get(q_id, '')
            review_items.append({
                'id': q_id,
                'question': q.get('question', ''),
                'options': q.get('options', {}),
                'correct': q.get('correct', ''),
                'user_answer': user_ans,
                'is_correct': user_ans == q.get('correct', ''),
                'explanation': q.get('explanation', ''),
            })

    return render(request, 'admin_panel/review_invite.html', {
        'invite': invite,
        'violations': violations,
        'audit_logs': audit_logs,
        'time_taken_seconds': time_taken_seconds,
        'review_items': review_items,
        'snapshots_enabled': getattr(settings, 'PROCTOR_SNAPSHOTS_ENABLED', False),
        'active_tab': 'hiring',
    })


@login_required
@user_passes_test(is_admin)
@require_POST
def decide_invite(request, invite_id):
    """
    State-machine enforced hiring decision:
      - approve / reject ONLY allowed on SUBMITTED invites.
      - approve below pass_mark requires written note.
      - reject requires written note.
      - reopen ONLY allowed on APPROVED / REJECTED invites.
    """
    invite = get_object_or_404(TeacherTestInvite, pk=invite_id)
    action = request.POST.get('action', '').strip()
    notes = request.POST.get('admin_notes', '').strip()

    if action == 'toggle_review':
        invite.show_review_to_teacher = not invite.show_review_to_teacher
        invite.save(update_fields=['show_review_to_teacher', 'updated_at'])
        messages.info(
            request,
            f"Teacher answer review visibility set to {'ON' if invite.show_review_to_teacher else 'OFF'}."
        )
        return redirect('admin_panel:review_invite', invite_id=invite.id)

    if action == 'reopen':
        if invite.status not in ('APPROVED', 'REJECTED'):
            messages.error(request, "Only APPROVED or REJECTED invites can be re-opened for review.")
            return redirect('admin_panel:review_invite', invite_id=invite.id)
        with transaction.atomic():
            invite.status = 'SUBMITTED'
            invite.save(update_fields=['status', 'updated_at'])
            if invite.test:
                invite.test.status = 'TAKEN'
                invite.test.save(update_fields=['status'])
            VerifiedTeacherSkill.objects.filter(test=invite).update(is_active=False)
            AuditLog.objects.create(
                admin=request.user,
                action=f"Re-opened invite {invite.test_code} ({invite.teacher_email}) for review.",
                target_table='teacher_test_invites',
                target_id=invite.id,
            )
            InviteAuditLog.objects.create(
                admin=request.user,
                action='test_reopened',
                invite=invite,
                notes=notes or 'Re-opened by admin',
            )
        messages.info(request, f"Invite {invite.test_code} re-opened for review.")
        return redirect('admin_panel:review_invite', invite_id=invite.id)

    # Approve / Reject require SUBMITTED state
    if invite.status != 'SUBMITTED':
        messages.error(
            request,
            f"Decision rejected: invite must be in SUBMITTED state (current: {invite.status})."
        )
        return redirect('admin_panel:review_invite', invite_id=invite.id)

    if action == 'approve':
        pct = invite.test.percentage if invite.test else 0.0
        if pct < invite.pass_mark and not notes:
            messages.error(
                request,
                f"Score ({pct:.0f}%) is below pass mark ({invite.pass_mark}%). A written note is required to approve."
            )
            return redirect('admin_panel:review_invite', invite_id=invite.id)

        with transaction.atomic():
            invite.status = 'APPROVED'
            invite.admin_notes = notes or 'Approved by Admin.'
            invite.save(update_fields=['status', 'admin_notes', 'updated_at'])

            if invite.test:
                invite.test.status = 'APPROVED'
                invite.test.admin_notes = invite.admin_notes
                invite.test.save(update_fields=['status', 'admin_notes'])

            matched_user = User.objects.filter(email__iexact=invite.teacher_email).first()
            VerifiedTeacherSkill.objects.update_or_create(
                teacher_email=invite.teacher_email,
                skill=invite.skill,
                defaults={
                    'user': matched_user,
                    'approved_by': request.user,
                    'test': invite,
                    'is_active': True,
                },
            )
            if matched_user:
                Notification.objects.create(
                    user=matched_user,
                    title=f"Verified Teacher: {invite.skill.title}",
                    message=f"Congratulations! You are now a verified teacher for {invite.skill.title} on Skill-Verse.",
                    type='achievement',
                    action_url='/profile/',
                    action_text='View Badge',
                )
            AuditLog.objects.create(
                admin=request.user,
                action=f"Approved & verified {invite.teacher_email} for skill '{invite.skill.title}' ({invite.test_code}).",
                target_table='teacher_test_invites',
                target_id=invite.id,
            )
            InviteAuditLog.objects.create(
                admin=request.user,
                action='test_approved',
                invite=invite,
                notes=invite.admin_notes,
            )

        name = invite.teacher_name or invite.teacher_email
        send_brevo_email(
            invite.teacher_email,
            name,
            f"Congratulations! You are Verified for {invite.skill.title} — Skill-Verse",
            f"<p>Hello <strong>{name}</strong>,</p><p>You passed the qualification review and are now a <strong>Verified Teacher</strong> for <strong>{invite.skill.title}</strong> on Skill-Verse!</p>",
            f"Hello {name},\n\nCongratulations! You are now a Verified Teacher for {invite.skill.title} on Skill-Verse.",
        )
        messages.success(request, f"Teacher {invite.teacher_email} APPROVED & verified for '{invite.skill.title}'!")
        return redirect('admin_panel:review_invite', invite_id=invite.id)

    elif action == 'reject':
        if not notes:
            messages.error(request, "A written note is required when rejecting a candidate.")
            return redirect('admin_panel:review_invite', invite_id=invite.id)

        with transaction.atomic():
            invite.status = 'REJECTED'
            invite.admin_notes = notes
            invite.save(update_fields=['status', 'admin_notes', 'updated_at'])

            if invite.test:
                invite.test.status = 'REJECTED'
                invite.test.admin_notes = notes
                invite.test.save(update_fields=['status', 'admin_notes'])

            AuditLog.objects.create(
                admin=request.user,
                action=f"Rejected {invite.teacher_email} for skill '{invite.skill.title}' ({invite.test_code}).",
                target_table='teacher_test_invites',
                target_id=invite.id,
            )
            InviteAuditLog.objects.create(
                admin=request.user,
                action='test_rejected',
                invite=invite,
                notes=notes,
            )

        name = invite.teacher_name or invite.teacher_email
        send_brevo_email(
            invite.teacher_email,
            name,
            f"Skill-Verse Qualification Update — {invite.skill.title}",
            f"<p>Hello <strong>{name}</strong>,</p><p>Thank you for taking the {invite.skill.title} exam. Your application was not approved at this time.</p><p><strong>Reviewer Note:</strong> {notes}</p><p>You may be re-invited after 7 days.</p>",
            f"Hello {name},\n\nYour application for {invite.skill.title} was not approved at this time.\nNote: {notes}\nYou may be re-invited after 7 days.",
        )
        messages.warning(request, f"Candidate {invite.teacher_email} rejected.")
        return redirect('admin_panel:review_invite', invite_id=invite.id)

    messages.error(request, "Invalid action.")
    return redirect('admin_panel:review_invite', invite_id=invite.id)


@login_required
@user_passes_test(is_admin)
def view_proctor_snapshot(request, violation_id):
    """Serve private proctoring snapshot ONLY to authenticated admins."""
    violation = get_object_or_404(TestViolation, pk=violation_id)
    if not violation.snapshot_path:
        raise Http404("No snapshot attached.")

    private_root = Path(getattr(settings, 'PRIVATE_MEDIA_ROOT', settings.BASE_DIR / 'private_media')).resolve()
    target = (private_root / violation.snapshot_path).resolve()

    if not target.is_relative_to(private_root) or not target.exists() or not target.is_file():
        raise Http404("Snapshot not found.")

    return FileResponse(open(target, 'rb'), content_type='image/jpeg')
