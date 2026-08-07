from .models import Feedback


class FeedbackService:

    @staticmethod
    def average_rating(teacher):

        feedbacks = Feedback.objects.filter(
            teacher=teacher
        )

        if not feedbacks.exists():
            return 0

        total = sum(f.rating for f in feedbacks)

        return round(total / feedbacks.count(), 2)