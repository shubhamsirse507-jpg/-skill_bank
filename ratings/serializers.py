"""
ratings/serializers.py
DRF serializers for ReviewRating.
"""
from rest_framework import serializers
from .models import ReviewRating


class ReviewRatingSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewed_user_username = serializers.CharField(source='reviewed_user.username', read_only=True)
    tag_list = serializers.ListField(source='tag_list', read_only=True)

    class Meta:
        model = ReviewRating
        fields = [
            'id', 'booking', 'reviewer', 'reviewer_username',
            'reviewed_user', 'reviewed_user_username',
            'rating', 'communication_rating', 'clarity_rating', 'punctuality_rating',
            'comment', 'tags', 'tag_list', 'would_recommend', 'created_at',
        ]
        read_only_fields = ['id', 'reviewer', 'created_at']
