from django.db import models


class Doubt(models.Model):
    # your fields
    pass


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