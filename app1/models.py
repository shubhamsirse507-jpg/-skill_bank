from django.db import models


class Doubt(models.Model):
    student_name = models.CharField(max_length=100, default="Student")
    title = models.CharField(max_length=200, default="General Doubt")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.title}"


class Booking(models.Model):
    student_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)

    def __str__(self):
        return self.student_name


class Notification(models.Model):
    message = models.CharField(max_length=255)


class VideoSession(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    student_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)
    meeting_id = models.CharField(max_length=100)
    meeting_link = models.URLField()