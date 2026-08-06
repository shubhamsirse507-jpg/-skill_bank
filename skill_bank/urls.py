from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("", include("authentication.urls")),
    path("auth/", include("authentication.urls")),

    # Profile
    path("profile/", include("profiles.urls")),

    # Dashboard
    path("dashboard/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)