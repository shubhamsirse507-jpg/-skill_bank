from django.db import models
from django.contrib.auth import get_user_model
from payments.models import Payment

User = get_user_model()


class Feedback(models.Model):

    RATING_CHOICES = (
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    )

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="feedback"
    )

    learner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="given_feedback"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_feedback"
    )

    rating = models.IntegerField(
        choices=RATING_CHOICES
    )

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.teacher.username} ({self.rating}⭐)"