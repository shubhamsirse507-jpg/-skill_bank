from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "learner",
        "teacher",
        "rating",
        "created_at",
    )

    search_fields = (
        "learner__username",
        "teacher__username",
    )

    list_filter = (
        "rating",
    )