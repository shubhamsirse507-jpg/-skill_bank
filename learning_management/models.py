from django.db import models
from course_management.models import Course


class Learning(models.Model):

    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    learner_name = models.CharField(max_length=100)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    progress = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Not Started'
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.learner_name} - {self.course.title}"