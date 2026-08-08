from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from skill_management.models import Skill, SkillCategory


from messaging.models import SkillExchange
from django.db.models import Q


@login_required
def dashboard(request):
    """User-facing dashboard home page."""
    user = request.user
    user_skills = Skill.objects.filter(user=user)
    recent_skills = Skill.objects.filter(status='approved').order_by('-created_at')[:6]

    skills_offered_count = Skill.objects.filter(user=user, skill_type='offered').count()
    skills_requested_count = Skill.objects.filter(user=user, skill_type='wanted').count()
    pending_requests_count = SkillExchange.objects.filter(receiver=user, status='pending').count()
    completed_swaps_count = SkillExchange.objects.filter(
        Q(requester=user) | Q(receiver=user),
        status='completed'
    ).count()

    categories = SkillCategory.objects.filter(is_active=True)[:8]

    return render(request, "user_dashboard/dashboard.html", {
        'user_skills': user_skills,
        'recent_skills': recent_skills,
        'skills_offered_count': skills_offered_count,
        'skills_requested_count': skills_requested_count,
        'pending_requests_count': pending_requests_count,
        'completed_swaps_count': completed_swaps_count,
        'categories': categories,
    })


def skill_list(request):
    """Lists approved platform skills."""
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(status='approved').select_related('category', 'user')

    if query:
        skills = skills.filter(title__icontains=query)

    return render(request, "user_dashboard/skill_list.html", {
        "skills": skills,
        "query": query,
    })


@login_required
def add_skill(request):
    """Creates a new skill for current user."""
    if request.method == "POST":
        title = request.POST.get("skill_name", "").strip() or request.POST.get("title", "").strip()
        category_id = request.POST.get("category_id") or request.POST.get("category")
        description = request.POST.get("description", "").strip()
        level = request.POST.get("level", "Beginner")

        if title:
            category = SkillCategory.objects.first()
            if category_id and category_id.isdigit():
                cat = SkillCategory.objects.filter(id=int(category_id)).first()
                if cat:
                    category = cat

            Skill.objects.create(
                user=request.user,
                category=category,
                title=title,
                description=description,
                level=level,
                status='approved'
            )
            messages.success(request, f"Skill '{title}' added successfully!")
            return redirect("skills")

    categories = SkillCategory.objects.filter(is_active=True)
    return render(request, "user_dashboard/add_skill.html", {"categories": categories})


@login_required
def live_session(request):
    return render(request, "user_dashboard/live_session.html")


@login_required
def chatbot_page(request):
    return render(request, "user_dashboard/chatbot.html")

chatbot = chatbot_page


def logout_user(request):
    logout(request)
    return redirect("login")


@login_required
def request_skill(request):
    """View to request a skill exchange with another user."""
    available_skills = Skill.objects.filter(status='approved').exclude(user=request.user).select_related('user', 'category')
    return render(request, "user_dashboard/request.html", {"available_skills": available_skills})