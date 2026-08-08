from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Admin HTML Pages
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.manage_users, name='user_management'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('skills/', views.manage_skills, name='manage_skills'),
    path('reports/', views.manage_reports, name='manage_reports'),
    path('monitoring/', views.platform_monitoring, name='platform_monitoring'),
    path('notice/post/', views.post_notice, name='post_notice'),

    # REST API Routes
    path('api/reports/', views.ReportListCreateView.as_view(), name='report-list'),
    path('api/reports/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('api/notices/', views.NoticeListCreateView.as_view(), name='notice-list'),
    path('api/notices/<int:pk>/', views.NoticeDetailView.as_view(), name='notice-detail'),
    path('api/audit-logs/', views.AuditLogListView.as_view(), name='audit-logs'),
]
