from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_skill_view, name='create_skill'),
    path('certificates/', views.my_certificates, name='my_certificates'),
    path('issue-certificate/', views.issue_certificate, name='issue_certificate'),
    path('certificate/<str:cert_id>/', views.certificate_detail, name='certificate_detail'),
    # Legacy alias
    path('certificates/<str:cert_id>/', views.certificate_detail, name='certificate_detail_legacy'),
]