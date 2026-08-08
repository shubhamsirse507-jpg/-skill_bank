from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Skill, SkillCategory


@login_required
def create_skill_view(request):
    """Web UI endpoint for a user to post a skill listing (offered or wanted)."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category_id')
        description = request.POST.get('description', '').strip()
        level = request.POST.get('level', 'Beginner')
        skill_type = request.POST.get('skill_type', 'offered')

        if not title or not category_id:
            messages.error(request, 'Title and category are required.')
            return redirect('search_skills')

        category = get_object_or_404(SkillCategory, id=category_id)

        skill = Skill.objects.create(
            user=request.user,
            category=category,
            title=title,
            description=description,
            level=level,
            skill_type=skill_type,
            status='approved'
        )

        messages.success(request, f"Skill '{skill.title}' posted successfully!")
        return redirect('profile')

    categories = SkillCategory.objects.filter(is_active=True)
    return render(request, 'skill_management/create_skill.html', {'categories': categories})