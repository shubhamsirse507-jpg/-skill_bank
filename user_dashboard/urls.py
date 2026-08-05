from django.urls import path
from . import views

urlpatterns = [
  
    path("dashboard/", views.dashboard, name="dashboard"),

    path("skills/", views.skill_list, name="skills"),

    path("add-skill/", views.add_skill, name="add_skill"),

     path("live-session/", views.live_session, name="live_session"),

    path("chatbot/", views.chatbot, name="chatbot"),

    path("logout/", views.logout_user, name="logout"),
]