from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
import os

from .models import PlatformReport, PlatformNotice, AuditLog
from skill_management.models import SkillCategory, Skill
from messaging.models import SkillExchange, Message
from ratings.models import ReviewRating


def is_admin(user):
    return user.is_authenticated and (
        user.is_staff or getattr(user, 'profile', None) and user.profile.role == 'admin'
    )


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main Admin Dashboard Overview"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_exchanges = SkillExchange.objects.count()
    completed_exchanges = SkillExchange.objects.filter(status='completed').count()
    total_reviews = ReviewRating.objects.count()
    pending_reports = PlatformReport.objects.filter(status='PENDING').count()
    total_categories = SkillCategory.objects.count()
    total_skills = Skill.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_reports = PlatformReport.objects.select_related('reported_by', 'reported_user').order_by('-created_at')[:5]
    recent_exchanges = SkillExchange.objects.select_related('requester', 'receiver').order_by('-created_at')[:5]
    recent_audit_logs = AuditLog.objects.select_related('admin').order_by('-created_at')[:8]

    categories = SkillCategory.objects.annotate(skill_count=Count('skills'))

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_exchanges': total_exchanges,
        'completed_exchanges': completed_exchanges,
        'total_reviews': total_reviews,
        'pending_reports': pending_reports,
        'total_categories': total_categories,
        'total_skills': total_skills,
        'recent_users': recent_users,
        'recent_reports': recent_reports,
        'recent_exchanges': recent_exchanges,
        'recent_audit_logs': recent_audit_logs,
        'categories': categories,
        'active_tab': 'dashboard',
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """User Management & Moderation"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'all')

    users = User.objects.annotate(
        requested_count=Count('requested_exchanges', distinct=True),
        provided_count=Count('received_exchanges', distinct=True),
        review_count=Count('reviews_given', distinct=True)
    ).order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'suspended':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)

    context = {
        'users': users,
        'query': query,
        'status_filter': status_filter,
        'active_tab': 'users',
    }
    return render(request, 'admin_panel/users.html', context)


@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """Suspend or Activate User Account"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        target_user.is_active = not target_user.is_active
        target_user.save()

        status_str = "activated" if target_user.is_active else "suspended"
        AuditLog.objects.create(
            admin=request.user,
            action=f"User {target_user.username} was {status_str}.",
            target_table="users",
            target_id=target_user.id
        )
        messages.success(request, f"User '{target_user.username}' has been successfully {status_str}.")

    return redirect('admin_panel:user_management')


@login_required
@user_passes_test(is_admin)
def manage_skills(request):
    """Manage Skill Categories and Platform Skills"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_category':
            category_name = request.POST.get('category_name', '').strip()
            icon_class = request.POST.get('icon_class', 'fa-solid fa-layer-group')
            description = request.POST.get('description', '')
            if category_name:
                cat, created = SkillCategory.objects.get_or_create(
                    category_name=category_name,
                    defaults={'icon_class': icon_class, 'description': description}
                )
                if created:
                    messages.success(request, f"Category '{category_name}' added successfully.")
                else:
                    messages.warning(request, f"Category '{category_name}' already exists.")

        elif action == 'add_skill':
            skill_name = request.POST.get('skill_name', '').strip()
            category_id = request.POST.get('category_id')
            demand = request.POST.get('demand_level', 'MEDIUM')
            description = request.POST.get('description', '')
            if skill_name and category_id:
                category = get_object_or_404(SkillCategory, pk=category_id)
                skill, created = Skill.objects.get_or_create(
                    title=skill_name,
                    category=category,
                    user=request.user,
                    defaults={'demand_level': demand, 'description': description, 'status': 'approved'}
                )
                if created:
                    messages.success(request, f"Skill '{skill_name}' added under '{category.category_name}'.")
                else:
                    messages.warning(request, f"Skill '{skill_name}' already exists.")

        return redirect('admin_panel:manage_skills')

    categories = SkillCategory.objects.prefetch_related('skills').annotate(skill_count=Count('skills'))
    skills = Skill.objects.select_related('category', 'user').order_by('category__category_name', 'title')

    context = {
        'categories': categories,
        'skills': skills,
        'active_tab': 'skills',
    }
    return render(request, 'admin_panel/skills.html', context)


@login_required
@user_passes_test(is_admin)
def manage_reports(request):
    """Moderation Queue & Abuse Reports"""
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        new_status = request.POST.get('status')
        action_note = request.POST.get('action_taken', '')

        report = get_object_or_404(PlatformReport, pk=report_id)
        report.status = new_status
        report.action_taken = action_note
        report.save()

        AuditLog.objects.create(
            admin=request.user,
            action=f"Updated Report #{report.id} to status '{new_status}'",
            target_table="reports",
            target_id=report.id
        )
        messages.success(request, f"Report #{report.id} status updated to '{new_status}'.")
        return redirect('admin_panel:manage_reports')

    status_filter = request.GET.get('status', 'all')
    reports = PlatformReport.objects.select_related('reported_by', 'reported_user').order_by('-created_at')

    if status_filter != 'all':
        reports = reports.filter(status=status_filter.upper())

    pending_count = PlatformReport.objects.filter(status='PENDING').count()
    in_review_count = PlatformReport.objects.filter(status='IN_REVIEW').count()
    resolved_count = PlatformReport.objects.filter(status='RESOLVED').count()
    dismissed_count = PlatformReport.objects.filter(status='DISMISSED').count()

    context = {
        'reports': reports,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'in_review_count': in_review_count,
        'resolved_count': resolved_count,
        'dismissed_count': dismissed_count,
        'active_tab': 'reports',
    }
    return render(request, 'admin_panel/reports.html', context)


@login_required
@user_passes_test(is_admin)
def platform_monitoring(request):
    """Platform Monitoring & System Announcements"""
    notices = PlatformNotice.objects.order_by('-created_at')

    total_messages = Message.objects.count()
    unread_messages = Message.objects.filter(is_read=False).count()

    context = {
        'notices': notices,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'active_tab': 'monitoring',
    }
    return render(request, 'admin_panel/monitoring.html', context)


@login_required
@user_passes_test(is_admin)
def post_notice(request):
    """Post Platform System Announcement"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        priority = request.POST.get('priority', 'MEDIUM')
        target_group = request.POST.get('target_group', 'ALL')

        if title and message:
            notice = PlatformNotice.objects.create(
                title=title,
                message=message,
                priority=priority,
                target_group=target_group
            )
            AuditLog.objects.create(
                admin=request.user,
                action=f"Published notice '{title}' [{priority}]",
                target_table="platform_notices",
                target_id=notice.id
            )
            messages.success(request, f"Platform Notice '{title}' has been broadcast successfully.")

    return redirect('admin_panel:platform_monitoring')


# Function aliases for template / URL backwards compatibility
user_management = manage_users
content_moderation = manage_reports
skills_categories = manage_skills


# ---------------------------------------------------------------------------
# AI Teacher Qualification Mock Test & Hiring Module (Admin Only)
# ---------------------------------------------------------------------------
from .models import TeacherMockTest
from .ai_generator import generate_ai_mock_test


@login_required
@user_passes_test(is_admin)
def admin_teacher_hiring(request):
    """
    Admin-only module for inspecting AI-generated mock test evaluations & hiring teachers.
    """
    mock_tests = TeacherMockTest.objects.select_related('teacher').all()
    return render(request, 'admin_panel/hiring.html', {
        'mock_tests': mock_tests,
        'active_tab': 'hiring',
    })


@login_required
def take_mock_test(request, test_id=None):
    """
    Teacher takes the AI-generated skill mock test.
    If no test exists for the skill, AI auto-generates one.
    """
    if test_id:
        mock_test = get_object_or_404(TeacherMockTest, id=test_id)
    else:
        skill_name = request.GET.get('skill', 'Python & Web Development')
        questions = generate_ai_mock_test(skill_name)
        mock_test = TeacherMockTest.objects.create(
            teacher=request.user,
            skill_name=skill_name,
            questions_json=questions,
            total_questions=len(questions)
        )

    if request.method == 'POST' and mock_test.status == 'PENDING':
        questions = mock_test.questions_json
        submitted_answers = {}
        correct_count = 0

        for q in questions:
            q_id = str(q['id'])
            ans = request.POST.get(f'q_{q_id}', '')
            submitted_answers[q_id] = ans
            if ans == q['correct']:
                correct_count += 1

        score_pct = (correct_count / len(questions)) * 100 if len(questions) > 0 else 0
        mock_test.answers_json = submitted_answers
        mock_test.score = correct_count
        mock_test.percentage = score_pct
        mock_test.status = 'TAKEN'
        mock_test.save()

        messages.success(request, f"Mock Test submitted! Your Score: {correct_count}/{len(questions)} ({score_pct:.0f}%). Under Admin Review.")
        return redirect('admin_panel:take_mock_test', test_id=mock_test.id)

    if mock_test.status != 'PENDING':
        answers = mock_test.answers_json or {}
        for q in mock_test.questions_json:
            q_id = str(q.get('id', ''))
            q['user_answer'] = answers.get(q_id, '')

    return render(request, 'admin_panel/take_mock_test.html', {
        'mock_test': mock_test,
    })


@login_required
@user_passes_test(is_admin)
def approve_hire_teacher(request, test_id):
    """
    Admin approves & hires teacher based on AI Mock Test evaluation.
    """
    mock_test = get_object_or_404(TeacherMockTest, id=test_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('admin_notes', '').strip()

        if action == 'approve':
            mock_test.status = 'APPROVED'
            mock_test.admin_notes = notes or "Approved by Admin based on Mock Test performance."
            mock_test.save()
            messages.success(request, f"Teacher '{mock_test.teacher.username}' has been APPROVED & HIRED on SkillBank!")

        elif action == 'reject':
            mock_test.status = 'REJECTED'
            mock_test.admin_notes = notes or "Rejected after review."
            mock_test.save()
            messages.warning(request, f"Teacher application for '{mock_test.teacher.username}' has been rejected.")

    return redirect('admin_panel:hiring')



# ---------------------------------------------------------------------------
# DRF API Views (REST endpoints for admin_panel resources)
# ---------------------------------------------------------------------------
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .serializers import PlatformReportSerializer, PlatformNoticeSerializer, AuditLogSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ReportListCreateView(generics.ListCreateAPIView):
    serializer_class = PlatformReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PlatformReport.objects.all()
        return PlatformReport.objects.filter(reported_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class ReportDetailView(generics.RetrieveUpdateAPIView):
    queryset = PlatformReport.objects.all()
    serializer_class = PlatformReportSerializer
    permission_classes = [IsAdminUser]


class NoticeListCreateView(generics.ListCreateAPIView):
    queryset = PlatformNotice.objects.filter(is_active=True)
    serializer_class = PlatformNoticeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can create notices.")
        serializer.save()


class NoticeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlatformNotice.objects.all()
    serializer_class = PlatformNoticeSerializer
    permission_classes = [IsAdminUser]


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]

