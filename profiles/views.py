import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from profiles.models import UserProfile
from skill_management.models import Skill
from authentication.constants import AUTH_BACKGROUND_VIDEO_URL, BRAND_LOGO_IMAGE_NAME

PRESET_AVATARS = [
    {'id': 'preset_1', 'name': 'Avatar Alex', 'url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex'},
    {'id': 'preset_2', 'name': 'Avatar Jordan', 'url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jordan'},
    {'id': 'preset_3', 'name': 'Bot TechWiz', 'url': 'https://api.dicebear.com/7.x/bottts/svg?seed=TechWiz'},
    {'id': 'preset_4', 'name': 'Avatar Sam', 'url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sam'},
    {'id': 'preset_5', 'name': 'Bot SkillHero', 'url': 'https://api.dicebear.com/7.x/bottts/svg?seed=SkillHero'},
    {'id': 'preset_6', 'name': 'Identicon Bank', 'url': 'https://api.dicebear.com/7.x/identicon/svg?seed=SkillBank'},
]


def calculate_completion_score(profile_obj):
    """Calculates profile completeness / matching readiness score (0-100%)."""
    score = 0
    if profile_obj.user.first_name and profile_obj.user.last_name:
        score += 15
    if profile_obj.headline:
        score += 15
    if profile_obj.bio and len(profile_obj.bio) >= 15:
        score += 15
    if profile_obj.city or profile_obj.country or profile_obj.location:
        score += 10
    if profile_obj.profile_image or profile_obj.avatar_preset_url:
        score += 15
    if profile_obj.user.skills.filter(skill_type='offered').exists():
        score += 15
    if profile_obj.user.skills.filter(skill_type='wanted').exists():
        score += 15
    if profile_obj.resume:
        score += 10
    return min(score, 100)


@login_required
def profile(request):
    """
    Unified view for user Profile UI.
    Database-backed CRUD operation on UserProfile.
    """
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'remove_resume':
            if profile_obj.resume:
                profile_obj.resume.delete(save=False)
                profile_obj.resume = None
                profile_obj.save()
            messages.success(request, 'Resume removed successfully.')
            return redirect('profile')

        # Update User fields
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.save()

        # Update UserProfile fields
        profile_obj.phone = request.POST.get('phone', '').strip()
        profile_obj.headline = request.POST.get('headline', '').strip()
        profile_obj.bio = request.POST.get('bio', '').strip()
        profile_obj.location = request.POST.get('location', '').strip() or request.POST.get('city', '').strip()
        profile_obj.city = request.POST.get('city', '').strip()
        profile_obj.country = request.POST.get('country', '').strip()
        profile_obj.work_preference = request.POST.get('work_preference', 'Remote')
        profile_obj.matching_goal = request.POST.get('matching_goal', 'Peer Skill Swap')

        # Privacy switches
        profile_obj.show_email = request.POST.get('show_email') == 'on'
        profile_obj.show_phone = request.POST.get('show_phone') == 'on'
        profile_obj.is_profile_public = request.POST.get('is_profile_public') == 'on'

        # Avatar selection
        avatar_type = request.POST.get('avatar_type', 'preset')
        if avatar_type == 'preset':
            selected_preset = request.POST.get('selected_preset_url', '')
            if selected_preset:
                profile_obj.avatar_preset_url = selected_preset
        elif avatar_type == 'upload' and request.FILES.get('avatar_file'):
            profile_obj.profile_image = request.FILES['avatar_file']

        # Resume upload
        if request.FILES.get('resume_file'):
            profile_obj.resume = request.FILES['resume_file']

        profile_obj.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    skills_offered = Skill.objects.filter(user=request.user, skill_type='offered')
    skills_desired = Skill.objects.filter(user=request.user, skill_type='wanted')

    score = calculate_completion_score(profile_obj)

    return render(request, 'profiles/profile.html', {
        'profile_obj': profile_obj,
        'profile': {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'username': request.user.username,
            'email': request.user.email,
            'phone': profile_obj.phone,
            'headline': profile_obj.headline,
            'bio': profile_obj.bio,
            'city': profile_obj.city,
            'country': profile_obj.country,
            'location': profile_obj.location,
            'work_preference': profile_obj.work_preference,
            'matching_goal': profile_obj.matching_goal,
            'show_email': profile_obj.show_email,
            'show_phone': profile_obj.show_phone,
            'is_profile_public': profile_obj.is_profile_public,
            'avatar_preset': profile_obj.avatar_preset_url,
            'avatar_upload_url': profile_obj.profile_image.url if profile_obj.profile_image else '',
            'resume_url': profile_obj.resume.url if profile_obj.resume else '',
            'resume_name': os.path.basename(profile_obj.resume.name) if profile_obj.resume else '',
        },
        'completion_score': score,
        'active_avatar_url': profile_obj.avatar_url,
        'preset_avatars': PRESET_AVATARS,
        'skills_offered': skills_offered,
        'skills_desired': skills_desired,
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
    })


def public_profile(request, username):
    """Publicly viewable user profile."""
    target_user = get_object_or_404(User, username=username)
    profile_obj, _ = UserProfile.objects.get_or_create(user=target_user)

    if not profile_obj.is_profile_public and request.user != target_user:
        messages.warning(request, 'This user profile is private.')
        return redirect('user_dashboard')

    skills_offered = Skill.objects.filter(user=target_user, skill_type='offered')
    skills_desired = Skill.objects.filter(user=target_user, skill_type='wanted')

    return render(request, 'profiles/profile_public.html', {
        'target_user': target_user,
        'profile_obj': profile_obj,
        'skills_offered': skills_offered,
        'skills_desired': skills_desired,
    })
