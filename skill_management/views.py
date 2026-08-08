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


from .models import SkillCertificate
from django.contrib.auth.models import User


@login_required
def issue_certificate(request):
    """
    Teacher issues a Skill Completion Certificate to a student.
    """
    if request.method == 'POST':
        student_username = request.POST.get('student_username', '').strip()
        skill_title = request.POST.get('skill_title', '').strip()
        grade = request.POST.get('grade_performance', 'Excellence (Passed)')
        remarks = request.POST.get('remarks', '').strip()

        student = User.objects.filter(username=student_username).first()
        if not student:
            messages.error(request, f"Student '{student_username}' not found.")
            return redirect('my_certificates')

        cert = SkillCertificate.objects.create(
            student=student,
            teacher=request.user,
            skill_title=skill_title,
            grade_performance=grade,
            remarks=remarks
        )
        messages.success(request, f"Certificate successfully issued to {student.username}!")
        from django.urls import reverse
        return redirect(reverse('certificate_detail', kwargs={'cert_id': cert.certificate_id}))

    students = User.objects.exclude(id=request.user.id)
    return render(request, 'skill_management/issue_certificate.html', {'students': students})


def certificate_detail(request, cert_id):
    """
    Publicly verifiable Skill Completion Certificate view.
    """
    certificate = get_object_or_404(SkillCertificate.objects.select_related('student', 'teacher'), certificate_id=cert_id)
    return render(request, 'skill_management/certificate_detail.html', {'cert': certificate})


@login_required
def my_certificates(request):
    """
    Student views all earned certificates & Teacher views issued ones.
    """
    earned = SkillCertificate.objects.filter(student=request.user)
    issued = SkillCertificate.objects.filter(teacher=request.user)
    return render(request, 'skill_management/my_certificates.html', {
        'earned': earned,
        'issued': issued,
    })