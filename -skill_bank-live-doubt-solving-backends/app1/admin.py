from django.contrib import admin
from .models import Doubt, Booking, Notification, VideoSession

admin.site.register(Doubt)
admin.site.register(Booking)
admin.site.register(Notification)
admin.site.register(VideoSession)