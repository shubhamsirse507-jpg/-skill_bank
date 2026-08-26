import logging
from django.shortcuts import render
from django.db.models import Q
from skill_management.models import Skill, SkillCategory
from profiles.models import UserProfile

logger = logging.getLogger(__name__)


def search_view(request):
    """
    Search & Matching service.
    Filter skills and users by keyword, category, level, skill_type, location, availability.
    Any DB error is caught and surfaced as an empty result set (avoids 500).
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    level = request.GET.get('level')
    skill_type = request.GET.get('type', 'offered')
    location = request.GET.get('location', '').strip()

    skills = []
    categories = []
    error_msg = None

    try:
        skills_qs = Skill.objects.select_related('category', 'user', 'user__profile').filter(status='approved')

        if skill_type in ['offered', 'wanted']:
            skills_qs = skills_qs.filter(skill_type=skill_type)

        if query:
            skills_qs = skills_qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__category_name__icontains=query) |
                Q(user__username__icontains=query)
            )

        if category_id:
            skills_qs = skills_qs.filter(category_id=category_id)

        if level in ['Beginner', 'Intermediate', 'Advanced']:
            skills_qs = skills_qs.filter(level=level)

        if location:
            skills_qs = skills_qs.filter(user__profile__location__icontains=location)

        # Force evaluation inside try block so DB errors are caught here
        skills = list(skills_qs)
    except Exception as e:
        logger.exception("search_view skill query failed: %s", e)
        error_msg = "Search is temporarily unavailable. Please try again shortly."
        skills = []

    try:
        categories = list(SkillCategory.objects.filter(is_active=True))
    except Exception as e:
        logger.exception("search_view category query failed: %s", e)
        categories = []

    context = {
        'skills': skills,
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
        'selected_level': level,
        'selected_type': skill_type,
        'selected_location': location,
        'error_msg': error_msg,
    }
    return render(request, 'search/search.html', context)
