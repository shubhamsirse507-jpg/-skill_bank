from django.db import models
from django.contrib.auth.models import User
from messaging.models import SkillExchange


class ReviewRating(models.Model):
    exchange = models.ForeignKey(SkillExchange, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='reviews_given', on_delete=models.CASCADE)
    reviewee = models.ForeignKey(User, related_name='reviews_received', on_delete=models.CASCADE)
    
    rating = models.IntegerField(default=5)  # Overall 1-5 stars
    communication_rating = models.IntegerField(default=5)
    clarity_rating = models.IntegerField(default=5)
    punctuality_rating = models.IntegerField(default=5)
    
    comment = models.TextField()
    tags = models.CharField(max_length=255, blank=True, help_text="Comma separated highlights (e.g. Great Communicator, Patient)")
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def __str__(self):
        return f"{self.rating}★ Review by {self.reviewer.username} for {self.reviewee.username}"

    class Meta:
        ordering = ['-created_at']
