from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Skill

def dashboard(request):
    return render(request, "user_dashboard/dashboard.html")


def skill_list(request):
    skills = Skill.objects.all()

    query = request.GET.get("q")

    if query:
        skills = skills.filter(skill_name__icontains=query)

    return render(request, "user_dashboard/skill_list.html", {
        "skills": skills
    })


def add_skill(request):

    if request.method == "POST":

        Skill.objects.create(
            skill_name=request.POST.get("skill_name"),
            category=request.POST.get("category"),
            description=request.POST.get("description"),
            level=request.POST.get("level"),
            offered_by=request.POST.get("offered_by"),
        )

        return redirect("skills")

    return render(request, "user_dashboard/add_skill.html")


def live_session(request):
    return render(request, "user_dashboard/live_session.html")


def chatbot_page(request):
    return render(request, "user_dashboard/chatbot.html")


def logout_user(request):
    logout(request)
    return redirect("login")

def chatbot(request):
    return render(request, "user_dashboard/chatbot.html")

def request_skill(request):
    return render(request, "user_dashboard/request.html")