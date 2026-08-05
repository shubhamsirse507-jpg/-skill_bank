from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from .models import Skill

# Create your views here.

def dashboard(request):
    return render(request, 'user_dashboard/dashboard.html')

def skill_list(request):
    return render(request, 'user_dashboard/skill_list.html')




def add_skill(request):

    if request.method == "POST":

        skill_name = request.POST.get("skill_name")
        category = request.POST.get("category")
        description = request.POST.get("description")

        Skill.objects.create(
            skill_name=skill_name,
            category=category,
            description=description
        )

        return redirect("skills")

    return render(request, "add_skill.html")


# ------------------------
# LIVE SESSION
# ------------------------

def live_session(request):
    return render(request, "user_dashboard/live_session.html")


# ------------------------
# CHATBOT
# ------------------------

def chatbot(request):

    message = request.GET.get("message", "").lower()

    if "python" in message:
        reply = "Python is a beginner-friendly programming language."

    elif "django" in message:
        reply = "Django is a Python web framework used to build websites."

    elif "html" in message:
        reply = "HTML is used to create web pages."

    elif "css" in message:
        reply = "CSS is used to design web pages."

    elif "hello" in message:
        reply = "Hello! 👋 How can I help you today?"

    else:
        reply = "Sorry, I don't know that yet."

    return JsonResponse({"reply": reply})


# ------------------------
# LOGOUT
# ------------------------

def logout_user(request):
    logout(request)
    return redirect("login")