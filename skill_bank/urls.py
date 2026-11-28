"""
Skill Exchange Platform — Root URL Configuration
Single canonical urls.py for the entire platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import search.views
import bookings.views
import payments.views
from admin_panel import teacher_test_views
from django.http import JsonResponse
from django.db import connection

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def health_check(request):
    """
    /health/ — Render health probe & diagnostic endpoint.
    Returns 200 JSON with DB status so we can confirm migrations ran.
    """
    import sys
    import django
    db_ok = False
    db_tables = []
    db_error = None
    try:
        db_tables = connection.introspection.table_names()
        db_ok = True
    except Exception as e:
        db_error = str(e)

    return JsonResponse({
        'status': 'ok' if db_ok else 'db_error',
        'python': sys.version,
        'django': django.get_version(),
        'debug': settings.DEBUG,
        'db_ok': db_ok,
        'db_error': db_error,
        'key_tables': {
            'django_session': 'django_session' in db_tables,
            'auth_user': 'auth_user' in db_tables,
            'profiles_userprofile': 'profiles_userprofile' in db_tables,
            'authentication_otpverification': 'authentication_otpverification' in db_tables,
        },
    }, status=200 if db_ok else 500)

# ---------------------------------------------------------------------------
# Swagger / OpenAPI schema
# ---------------------------------------------------------------------------
schema_view = get_schema_view(
    openapi.Info(
        title="Skill Exchange Platform API",
        default_version='v1',
        description=(
            "REST API powering the Skill Exchange Platform web app and mobile clients. "
            "Authenticate with Bearer JWT tokens obtained from /api/v1/auth/login/."
        ),
        contact=openapi.Contact(email="dev@skillexchange.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # -----------------------------------------------------------------------
    # Health check / Render deploy probe
    # -----------------------------------------------------------------------
    path('health/', health_check, name='health_check'),

    # -----------------------------------------------------------------------
    # Django Admin
    # -----------------------------------------------------------------------
    path('django-admin/', admin.site.urls),

    # -----------------------------------------------------------------------
    # Web UI — Template-rendered views
    # -----------------------------------------------------------------------
    path('', include('authentication.urls')),               # landing, login, register, OTP
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('user/', include('user_dashboard.urls')),
    path('profile/', include('profiles.urls')),
    path('notifications/', include('notifications.urls')),
    path('messaging/', include('messaging.urls')),
    path('ratings/', include('ratings.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    # Public invite-token Teacher Exam routes (no login required; token + session guarded)
    path('teacher-test/<str:token>/', teacher_test_views.teacher_test_entry, name='teacher_test_entry'),
    path('teacher-test/<str:token>/instructions/', teacher_test_views.teacher_test_instructions, name='teacher_test_instructions'),
    path('teacher-test/<str:token>/start/', teacher_test_views.teacher_test_start, name='teacher_test_start'),
    path('teacher-test/<str:token>/exam/', teacher_test_views.teacher_test_exam, name='teacher_test_exam'),
    path('teacher-test/<str:token>/question/<int:idx>/', teacher_test_views.teacher_test_question, name='teacher_test_question'),
    path('teacher-test/<str:token>/answer/', teacher_test_views.teacher_test_answer, name='teacher_test_answer'),
    path('teacher-test/<str:token>/submit/', teacher_test_views.teacher_test_submit, name='teacher_test_submit'),
    path('teacher-test/<str:token>/proctor-event/', teacher_test_views.teacher_test_proctor_event, name='teacher_test_proctor_event'),
    path('skills/', include('skill_management.urls')),
    path('search/', include('search.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('chat/', include('chatboat.urls')),

    # Direct top-level shortcuts matching Lovable app URL structure
    path('browse/', search.views.search_view, name='browse'),
    path('batches/', bookings.views.batches_view, name='batches_direct'),
    path('live/', bookings.views.live_sessions_view, name='live_direct'),
    path('doubt/', bookings.views.doubt_view, name='doubt_direct'),
    path('wallet/', payments.views.wallet_view, name='wallet_direct'),
    path('receipts/', payments.views.my_receipts, name='receipts_direct'),



    # -----------------------------------------------------------------------
    # REST API v1
    # -----------------------------------------------------------------------
    path('api/v1/', include('api.urls')),

    # -----------------------------------------------------------------------
    # Swagger / ReDoc docs
    # -----------------------------------------------------------------------
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
    path('api/v1/schema.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
