from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('skills/', views.manage_skills, name='manage_skills'),
    path('reports/', views.manage_reports, name='manage_reports'),
    path('monitoring/', views.platform_monitoring, name='platform_monitoring'),
    path('notices/post/', views.post_notice, name='post_notice'),
]
