from django.contrib import admin
from .models import Earning


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "teacher",
        "total_amount",
        "commission",
        "teacher_earning",
        "payment_status",
    )

    search_fields = (
        "teacher__username",
    )

    list_filter = (
        "payment_status",
    )