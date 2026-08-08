from django.shortcuts import render
from django.db.models import Q
from skill_management.models import Skill, SkillCategory
from profiles.models import UserProfile


def search_view(request):
    """
    Search & Matching service.
    Filter skills and users by keyword, category, level, skill_type, location, availability.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    level = request.GET.get('level')
    skill_type = request.GET.get('type', 'offered')
    location = request.GET.get('location', '').strip()

    skills = Skill.objects.select_related('category', 'user', 'user__profile').filter(status='approved')

    if skill_type in ['offered', 'wanted']:
        skills = skills.filter(skill_type=skill_type)

    if query:
        skills = skills.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__category_name__icontains=query) |
            Q(user__username__icontains=query)
        )

    if category_id:
        skills = skills.filter(category_id=category_id)

    if level in ['Beginner', 'Intermediate', 'Advanced']:
        skills = skills.filter(level=level)

    if location:
        skills = skills.filter(user__profile__location__icontains=location)

    categories = SkillCategory.objects.filter(is_active=True)

    context = {
        'skills': skills,
        'categories': categories,
        'query': query,
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
        'selected_level': level,
        'selected_type': skill_type,
        'selected_location': location,
    }
    return render(request, 'search/search.html', context)
