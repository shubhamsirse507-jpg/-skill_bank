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

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
