from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
import os

from .models import SkillCategory, PlatformSkill, PlatformReport, PlatformNotice, AuditLog
from messaging.models import SkillExchange, Message
from ratings.models import ReviewRating


def admin_dashboard(request):
    """Main Admin Dashboard Overview"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_exchanges = SkillExchange.objects.count()
    completed_exchanges = SkillExchange.objects.filter(status='COMPLETED').count()
    total_reviews = ReviewRating.objects.count()
    pending_reports = PlatformReport.objects.filter(status='PENDING').count()
    total_categories = SkillCategory.objects.count()
    total_skills = PlatformSkill.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_reports = PlatformReport.objects.select_related('reporter', 'reported_user').order_by('-created_at')[:5]
    recent_exchanges = SkillExchange.objects.select_related('requester', 'provider').order_by('-created_at')[:5]
    recent_audit_logs = AuditLog.objects.select_related('actor').order_by('-created_at')[:8]

    # Category Breakdown
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


def manage_users(request):
    """User Management & Moderation"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'all')

    users = User.objects.annotate(
        requested_count=Count('requested_exchanges', distinct=True),
        provided_count=Count('provided_exchanges', distinct=True),
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


def toggle_user_status(request, user_id):
    """Suspend or Activate User Account"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        target_user.is_active = not target_user.is_active
        target_user.save()

        status_str = "activated" if target_user.is_active else "suspended"
        actor = request.user if request.user.is_authenticated else None
        AuditLog.objects.create(
            actor=actor,
            action=f"User {target_user.username} was {status_str}.",
            target=target_user.username
        )
        messages.success(request, f"User '{target_user.username}' has been successfully {status_str}.")

    return redirect('manage_users')


def manage_skills(request):
    """Manage Skill Categories and Platform Skills"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_category':
            name = request.POST.get('category_name')
            icon_class = request.POST.get('icon_class', 'fa-solid fa-layer-group')
            description = request.POST.get('description', '')
            if name:
                category, created = SkillCategory.objects.get_or_create(
                    name=name,
                    defaults={'icon_class': icon_class, 'description': description}
                )
                if created:
                    messages.success(request, f"Category '{name}' added successfully.")
                else:
                    messages.warning(request, f"Category '{name}' already exists.")

        elif action == 'add_skill':
            skill_name = request.POST.get('skill_name')
            category_id = request.POST.get('category_id')
            demand = request.POST.get('demand_level', 'MEDIUM')
            description = request.POST.get('description', '')
            if skill_name and category_id:
                category = get_object_or_404(SkillCategory, pk=category_id)
                skill, created = PlatformSkill.objects.get_or_create(
                    name=skill_name,
                    category=category,
                    defaults={'demand_level': demand, 'description': description}
                )
                if created:
                    messages.success(request, f"Skill '{skill_name}' added under '{category.name}'.")
                else:
                    messages.warning(request, f"Skill '{skill_name}' already exists.")

        return redirect('manage_skills')

    categories = SkillCategory.objects.prefetch_related('skills').annotate(skill_count=Count('skills'))
    skills = PlatformSkill.objects.select_related('category').order_by('category__name', 'name')

    context = {
        'categories': categories,
        'skills': skills,
        'active_tab': 'skills',
    }
    return render(request, 'admin_panel/skills.html', context)


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

        actor = request.user if request.user.is_authenticated else None
        AuditLog.objects.create(
            actor=actor,
            action=f"Updated Report #{report.id} to status '{new_status}'",
            target=f"Report #{report.id}"
        )
        messages.success(request, f"Report #{report.id} status updated to '{new_status}'.")
        return redirect('manage_reports')

    status_filter = request.GET.get('status', 'all')
    reports = PlatformReport.objects.select_related('reporter', 'reported_user').order_by('-created_at')

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


def platform_monitoring(request):
    """Platform Monitoring, Server Metrics & System Announcements"""
    notices = PlatformNotice.objects.order_by('-created_at')

    # Metrics computation
    total_messages = Message.objects.count()
    unread_messages = Message.objects.filter(is_read=False).count()
    
    # DB File metric
    db_size_mb = 0.22
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
    if os.path.exists(db_path):
        db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2)

    context = {
        'notices': notices,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'db_size_mb': db_size_mb,
        'active_tab': 'monitoring',
    }
    return render(request, 'admin_panel/monitoring.html', context)


def post_notice(request):
    """Post Platform System Announcement"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        priority = request.POST.get('priority', 'MEDIUM')
        target_group = request.POST.get('target_group', 'ALL')

        if title and message:
            notice = PlatformNotice.objects.create(
                title=title,
                message=message,
                priority=priority,
                target_group=target_group
            )
            actor = request.user if request.user.is_authenticated else None
            AuditLog.objects.create(
                actor=actor,
                action=f"Published notice '{title}' [{priority}]",
                target="Platform Announcement"
            )
            messages.success(request, f"Platform Notice '{title}' has been broadcast successfully.")

    return redirect('platform_monitoring')
