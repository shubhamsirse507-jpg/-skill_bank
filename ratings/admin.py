from django.contrib import admin
from .models import ReviewRating


@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'reviewed_user', 'rating', 'would_recommend', 'created_at')
    list_filter = ('rating', 'would_recommend')
    search_fields = ('reviewer__username', 'reviewed_user__username', 'comment')
