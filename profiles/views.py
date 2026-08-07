import os
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from authentication.constants import AUTH_BACKGROUND_VIDEO_URL, BRAND_LOGO_IMAGE_NAME

PRESET_AVATARS = [
    {'id': 'preset_1', 'name': 'Avatar Alex', 'url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex'},
    {'id': 'preset_2', 'name': 'Avatar Jordan', 'url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jordan'},
    {'id': 'preset_3', 'name': 'Bot TechWiz', 'url': 'https://api.dicebear.com/7.x/bottts/svg?seed=TechWiz'},
    {'id': 'preset_4', 'name': 'Avatar Sam', 'url': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sam'},
    {'id': 'preset_5', 'name': 'Bot SkillHero', 'url': 'https://api.dicebear.com/7.x/bottts/svg?seed=SkillHero'},
    {'id': 'preset_6', 'name': 'Identicon Bank', 'url': 'https://api.dicebear.com/7.x/identicon/svg?seed=SkillBank'},
]

SKILL_SUGGESTIONS = [
    'Python', 'Django', 'React.js', 'Vue.js', 'TypeScript', 'Node.js',
    'Machine Learning', 'Data Science', 'Docker', 'Kubernetes', 'Figma / UI Design',
    'Cybersecurity', 'SQL Databases', 'GraphQL', 'AWS Cloud', 'Mobile Development (Flutter)'
]


def calculate_completion_score(profile):
    """Calculates profile completeness / matching readiness score (0-100%)."""
    score = 0
    if profile.get('first_name') and profile.get('last_name'):
        score += 15
    if profile.get('headline'):
        score += 15
    if profile.get('bio') and len(profile.get('bio', '')) >= 15:
        score += 15
    if profile.get('city') or profile.get('country'):
        score += 10
    if profile.get('avatar_preset') or profile.get('avatar_upload_url'):
        score += 15
    if profile.get('skills_offered') and len(profile.get('skills_offered')) > 0:
        score += 15
    if profile.get('skills_desired') and len(profile.get('skills_desired')) > 0:
        score += 15
    if profile.get('resume_url'):
        score += 10
    return min(score, 100)


def profile(request):
    """
    Single unified view for Profile UI.
    Handles viewing and editing user profile, photo upload, resume upload, skills, and privacy switches.
    """
    if 'profile_data' not in request.session:
        request.session['profile_data'] = {
            'first_name': '',
            'last_name': '',
            'username': request.user.username if request.user.is_authenticated else 'user',
            'email': request.user.email if request.user.is_authenticated else '',
            'phone': '',
            'headline': '',
            'bio': '',
            'city': '',
            'country': '',
            'work_preference': 'Remote',
            'avatar_type': 'preset',
            'avatar_preset': 'https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero',
            'avatar_upload_url': '',
            'resume_url': '',
            'resume_name': '',
            'show_email': True,
            'show_phone': False,
            'is_profile_public': True,
            'skills_offered': [],
            'skills_desired': [],
            'matching_goal': 'Peer Skill Swap',
        }

    profile_data = request.session['profile_data']

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'remove_resume':
            profile_data['resume_url'] = ''
            profile_data['resume_name'] = ''
            request.session['profile_data'] = profile_data
            request.session.modified = True
            messages.success(request, 'Resume removed successfully.')
            return redirect('profile')

        # Update text fields
        profile_data['first_name'] = request.POST.get('first_name', '').strip()
        profile_data['last_name'] = request.POST.get('last_name', '').strip()
        profile_data['phone'] = request.POST.get('phone', '').strip()
        profile_data['headline'] = request.POST.get('headline', '').strip()
        profile_data['bio'] = request.POST.get('bio', '').strip()
        profile_data['city'] = request.POST.get('city', '').strip()
        profile_data['country'] = request.POST.get('country', '').strip()
        profile_data['work_preference'] = request.POST.get('work_preference', 'Remote')
        profile_data['matching_goal'] = request.POST.get('matching_goal', 'Peer Skill Swap')

        # Privacy switches
        profile_data['show_email'] = request.POST.get('show_email') == 'on'
        profile_data['show_phone'] = request.POST.get('show_phone') == 'on'
        profile_data['is_profile_public'] = request.POST.get('is_profile_public') == 'on'

        # Avatar selection
        avatar_type = request.POST.get('avatar_type', 'preset')
        profile_data['avatar_type'] = avatar_type
        if avatar_type == 'preset':
            selected_preset = request.POST.get('selected_preset_url', '')
            if selected_preset:
                profile_data['avatar_preset'] = selected_preset
        elif avatar_type == 'upload' and request.FILES.get('avatar_file'):
            avatar_file = request.FILES['avatar_file']
            fs = FileSystemStorage(
                location=os.path.join(settings.MEDIA_ROOT, 'profile_photos'),
                base_url=f'{settings.MEDIA_URL}profile_photos/'
            )
            filename = fs.save(avatar_file.name, avatar_file)
            profile_data['avatar_upload_url'] = f'{settings.MEDIA_URL}profile_photos/{filename}'

        # Resume upload
        if request.FILES.get('resume_file'):
            resume_file = request.FILES['resume_file']
            fs_resume = FileSystemStorage(
                location=os.path.join(settings.MEDIA_ROOT, 'resumes'),
                base_url=f'{settings.MEDIA_URL}resumes/'
            )
            res_filename = fs_resume.save(resume_file.name, resume_file)
            profile_data['resume_url'] = f'{settings.MEDIA_URL}resumes/{res_filename}'
            profile_data['resume_name'] = resume_file.name

        # Skills Offered & Desired JSON
        try:
            skills_offered_raw = request.POST.get('skills_offered_json', '[]')
            profile_data['skills_offered'] = json.loads(skills_offered_raw)
        except Exception:
            pass

        try:
            skills_desired_raw = request.POST.get('skills_desired_json', '[]')
            profile_data['skills_desired'] = json.loads(skills_desired_raw)
        except Exception:
            pass

        request.session['profile_data'] = profile_data
        request.session.modified = True

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    score = calculate_completion_score(profile_data)
    active_avatar_url = profile_data['avatar_upload_url'] if profile_data['avatar_type'] == 'upload' and profile_data['avatar_upload_url'] else profile_data['avatar_preset']

    return render(request, 'profiles/profile.html', {
        'profile': profile_data,
        'completion_score': score,
        'active_avatar_url': active_avatar_url,
        'preset_avatars': PRESET_AVATARS,
        'skill_suggestions': SKILL_SUGGESTIONS,
        'bg_video_url': AUTH_BACKGROUND_VIDEO_URL,
        'brand_logo_image_name': BRAND_LOGO_IMAGE_NAME,
    })
