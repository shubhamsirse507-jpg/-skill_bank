from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication Module
    path("", include("authentication.urls")),
    path("auth/", include("authentication.urls")),

    # Dashboard Module
    path("dashboard/", include("dashboard.urls")),
]