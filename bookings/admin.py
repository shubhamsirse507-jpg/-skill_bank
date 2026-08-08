from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'scheduled_date', 'start_time', 'end_time', 'meeting_mode', 'status')
    list_filter = ('meeting_mode', 'status', 'scheduled_date')
    search_fields = ('request__title', 'request__requester__username', 'request__receiver__username')
