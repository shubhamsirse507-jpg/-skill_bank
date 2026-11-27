"""
ratings/serializers.py
DRF serializers for ReviewRating.
"""
from rest_framework import serializers
from .models import ReviewRating


def validate_star_score(value):
    if not (1 <= value <= 5):
        raise serializers.ValidationError("Rating must be between 1 and 5.")
    return value


class ReviewRatingSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewed_user_username = serializers.CharField(source='reviewed_user.username', read_only=True)
    tag_list = serializers.ReadOnlyField()

    rating = serializers.IntegerField(validators=[validate_star_score])
    communication_rating = serializers.IntegerField(default=5, validators=[validate_star_score])
    clarity_rating = serializers.IntegerField(default=5, validators=[validate_star_score])
    punctuality_rating = serializers.IntegerField(default=5, validators=[validate_star_score])

    class Meta:
        model = ReviewRating
        fields = [
            'id', 'booking', 'reviewer', 'reviewer_username',
            'reviewed_user', 'reviewed_user_username',
            'rating', 'communication_rating', 'clarity_rating', 'punctuality_rating',
            'comment', 'tags', 'tag_list', 'would_recommend', 'created_at',
        ]
        read_only_fields = ['id', 'reviewer', 'reviewed_user', 'created_at']
