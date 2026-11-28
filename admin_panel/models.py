"""
admin_panel/models.py
Spec tables: reports, admin_logs, platform_notices, teacher hiring system.
"""

import secrets
import string
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import datetime


class PlatformReport(models.Model):
    """
    Spec table: reports
    Platform moderation reports.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('IN_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]

    REASON_CHOICES = [
        ('SPAM', 'Spam or Unsolicited Promotion'),
        ('HARASSMENT', 'Harassment or Abusive Behavior'),
        ('FAKE_PROFILE', 'Fake Profile or Misrepresentation'),
        ('INAPPROPRIATE', 'Inappropriate Content'),
        ('OTHER', 'Other Violation'),
    ]

    # Spec: reported_by (was: reporter)
    reported_by = models.ForeignKey(
        User, related_name='submitted_reports', on_delete=models.CASCADE
    )
    reported_user = models.ForeignKey(
        User, related_name='reports_against', on_delete=models.CASCADE,
        null=True, blank=True
    )
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default='OTHER')
    # Spec: description (was: details)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    action_taken = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} - {self.get_reason_display()} ({self.status})"


class PlatformNotice(models.Model):
    """Platform system announcements broadcast to users."""

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    TARGET_CHOICES = [
        ('ALL', 'All Users'),
        ('TEACHERS', 'Mentors / Teachers'),
        ('LEARNERS', 'Learners'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    target_group = models.CharField(max_length=20, choices=TARGET_CHOICES, default='ALL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'platform_notices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notice: {self.title} [{self.priority}]"


class AuditLog(models.Model):
    """
    Spec table: admin_logs
    Audit logging for admin actions.
    """

    # Spec: admin_id (was: actor)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=200)
    # Spec: split target into target_table and target_id
    target_table = models.CharField(max_length=100, blank=True, default='')
    target_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')}: {self.admin} - {self.action}"


class TeacherMockTest(models.Model):
    """
    AI-Generated Qualification Mock Test for Teacher Hiring (Admin Only).
    Now linked to TeacherTestInvite (Phase 2+).
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Test'),
        ('TAKEN', 'Test Taken - Awaiting Admin Review'),
        ('APPROVED', 'Approved & Hired'),
        ('REJECTED', 'Rejected'),
    ]

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='mock_tests',
        null=True, blank=True,
        help_text='Null for invite-based tests where teacher has no account'
    )
    skill_name = models.CharField(max_length=150)
    skill = models.ForeignKey(
        'skill_management.Skill', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='mock_tests',
        help_text='FK to canonical Skill; preferred over free-text skill_name'
    )
    skill_level = models.CharField(max_length=50, default='Intermediate')
    questions_json = models.JSONField(default=list)
    answers_json = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=10)
    percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'teacher_mock_tests'
        ordering = ['-created_at']

    def __str__(self):
        teacher_label = self.teacher.username if self.teacher else 'invite-only'
        return f"Mock Test for {teacher_label} - {self.skill_name} [{self.status}]"


# ---------------------------------------------------------------------------
# Phase 2+: Invite-based teacher exam system
# ---------------------------------------------------------------------------

def _default_expires():
    return timezone.now() + datetime.timedelta(days=3)


def _gen_test_code():
    """Short human-readable code like SB-4821."""
    digits = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"SB-{digits}"


def _gen_token():
    return secrets.token_urlsafe(32)


def _gen_password(length=10):
    """Random password — only used to return plaintext once at invite creation."""
    alphabet = string.ascii_letters + string.digits + '!@#$'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class TeacherTestInvite(models.Model):
    """
    Admin-issued invitation for a teacher to take a qualification exam.
    The invite carries auth credentials (test_code + hashed password).
    Teachers do NOT need a Skill-Verse account.
    """
    STATUS_CHOICES = [
        ('INVITED', 'Invited'),
        ('STARTED', 'Test Started'),
        ('SUBMITTED', 'Submitted — Awaiting Review'),
        ('EXPIRED', 'Expired'),
        ('REVOKED', 'Revoked by Admin'),
        ('LOCKED', 'Locked — Too Many Failed Attempts'),
        ('APPROVED', 'Approved & Hired'),
        ('REJECTED', 'Rejected'),
    ]

    teacher_email = models.EmailField(db_index=True)
    teacher_name = models.CharField(max_length=200, blank=True, default='')
    skill = models.ForeignKey(
        'skill_management.Skill', on_delete=models.PROTECT,
        related_name='test_invites'
    )
    skill_level = models.CharField(max_length=50, default='Intermediate')

    # Auth credentials (never store token or password plaintext after creation)
    test_code = models.CharField(max_length=10, default=_gen_test_code)
    token = models.CharField(max_length=64, unique=True, db_index=True, default=_gen_token)
    password_hash = models.CharField(max_length=256)  # make_password result

    # Exam config
    pass_mark = models.IntegerField(default=60, help_text='Minimum % to pass')
    time_limit_minutes = models.IntegerField(default=20)
    question_count = models.IntegerField(default=10)
    expires_at = models.DateTimeField(default=_default_expires)

    # State
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INVITED')
    failed_attempts = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # Proctoring
    violation_count = models.IntegerField(default=0)
    proctoring_skipped = models.BooleanField(
        default=False,
        help_text='True if camera was unavailable and admin allowed no-camera'
    )

    # Relations
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='issued_invites'
    )
    test = models.OneToOneField(
        TeacherMockTest, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invite'
    )
    admin_notes = models.TextField(blank=True, default='')
    show_review_to_teacher = models.BooleanField(
        default=False,
        help_text='Admin can enable showing answers & explanations to the teacher after decision'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_test_invites'
        ordering = ['-created_at']

    def __str__(self):
        return f"Invite {self.test_code} → {self.teacher_email} [{self.status}]"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def deadline(self):
        """Server-enforced submission deadline (None until started)."""
        if self.started_at:
            return self.started_at + datetime.timedelta(minutes=self.time_limit_minutes)
        return None

    @property
    def is_past_deadline(self):
        if self.deadline is None:
            return False
        return timezone.now() > self.deadline + datetime.timedelta(seconds=10)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password_hash)

    @classmethod
    def create_invite(cls, teacher_email, teacher_name, skill, skill_level,
                      pass_mark, time_limit_minutes, question_count,
                      expires_at, created_by):
        """
        Factory: create invite with a fresh token + hashed random password.
        Returns (invite_instance, plaintext_password) — plaintext shown ONCE to admin.
        """
        raw_password = _gen_password(10)
        invite = cls(
            teacher_email=teacher_email,
            teacher_name=teacher_name,
            skill=skill,
            skill_level=skill_level,
            pass_mark=pass_mark,
            time_limit_minutes=time_limit_minutes,
            question_count=question_count,
            expires_at=expires_at,
            created_by=created_by,
            password_hash=make_password(raw_password),
        )
        invite.save()
        return invite, raw_password

    def regenerate_credentials(self):
        """
        Regenerate token and password (resend flow).
        Returns new plaintext password — shown ONCE.
        """
        raw_password = _gen_password(10)
        self.token = _gen_token()
        self.test_code = _gen_test_code()
        self.password_hash = make_password(raw_password)
        self.failed_attempts = 0
        self.status = 'INVITED'
        self.save()
        return raw_password


class QuestionBank(models.Model):
    """
    Per-skill question bank.  Seeds via management command seed_question_bank.
    """
    skill = models.ForeignKey(
        'skill_management.Skill', on_delete=models.CASCADE,
        null=True, blank=True, related_name='question_banks',
        help_text='Null = generic teaching-quality bank'
    )
    # Keyword slug for matching (e.g. "python", "guitar", "design")
    skill_slug = models.CharField(
        max_length=100, db_index=True,
        help_text='Lowercase keyword; whole-word matching against skill title'
    )
    description = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'question_banks'
        ordering = ['skill_slug']

    def __str__(self):
        return f"QuestionBank: {self.skill_slug}"


class Question(models.Model):
    """Single MCQ inside a QuestionBank."""
    bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    explanation = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questions'
        ordering = ['id']

    def __str__(self):
        return f"Q#{self.id}: {self.question_text[:60]}"

    def as_safe_dict(self, shuffled_index: int):
        """Return question data WITHOUT the correct answer (safe for browser)."""
        return {
            'idx': shuffled_index,
            'id': self.id,
            'question': self.question_text,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d,
            },
        }


class TestViolation(models.Model):
    """Proctoring event recorded during the exam."""
    TYPE_CHOICES = [
        ('no_face', 'No Face Detected'),
        ('multiple_faces', 'Multiple Faces'),
        ('head_turn', 'Sustained Head Turn'),
        ('body_out', 'Body Out of Frame'),
        ('phone_detected', 'Phone Detected'),
        ('tab_switch', 'Tab Switch / Focus Lost'),
        ('fullscreen_exit', 'Fullscreen Exited'),
        ('copy_attempt', 'Copy/Paste Attempt'),
    ]

    invite = models.ForeignKey(
        TeacherTestInvite, on_delete=models.CASCADE, related_name='violations'
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    started_at = models.DateTimeField(default=timezone.now)
    duration_seconds = models.FloatField(default=0.0)
    snapshot_path = models.CharField(
        max_length=500, blank=True, default='',
        help_text='Relative path under PRIVATE_MEDIA_ROOT; empty if snapshots disabled'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_violations'
        ordering = ['started_at']

    def __str__(self):
        return f"Violation({self.type}) invite={self.invite_id} at {self.started_at}"


class VerifiedTeacherSkill(models.Model):
    """
    Per-skill verified flag for a teacher.
    Created in a transaction when admin APPROVES a TeacherTestInvite.
    A teacher can be verified for Python but not Guitar.
    """
    # Either a registered user or just an email (invite-only)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='verified_skills'
    )
    teacher_email = models.EmailField(db_index=True)
    skill = models.ForeignKey(
        'skill_management.Skill', on_delete=models.CASCADE,
        related_name='verified_teachers'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='approved_teacher_skills'
    )
    test = models.OneToOneField(
        TeacherTestInvite, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_skill'
    )
    approved_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'verified_teacher_skills'
        unique_together = [('teacher_email', 'skill')]
        ordering = ['-approved_at']

    def __str__(self):
        return f"Verified: {self.teacher_email} → {self.skill.title}"


class InviteAuditLog(models.Model):
    """Fine-grained audit log for every admin action on invites."""
    ACTION_CHOICES = [
        ('invite_created', 'Invite Created'),
        ('invite_revoked', 'Invite Revoked'),
        ('invite_resent', 'Invite Resent'),
        ('invite_extended', 'Invite Extended'),
        ('test_started', 'Test Started'),
        ('test_submitted', 'Test Submitted'),
        ('test_approved', 'Test Approved'),
        ('test_rejected', 'Test Rejected'),
        ('test_reopened', 'Test Re-opened for Review'),
        ('invite_locked', 'Invite Locked — Brute Force'),
    ]

    admin = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invite_audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    invite = models.ForeignKey(
        TeacherTestInvite, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs'
    )
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invite_audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} by {self.admin} on invite {self.invite_id}"


