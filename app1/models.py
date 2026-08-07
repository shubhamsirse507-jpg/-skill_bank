from django.db import models

# Live Doubt Solving Module
class Doubt(models.Model):
    student_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    question = models.TextField()
    file = models.FileField(upload_to='doubts/', blank=True, null=True)
    answer = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return self.student_name


# Booking & Session Management Module
class Booking(models.Model):
    student_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)
    session_date = models.DateField()
    session_time = models.TimeField()
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='Booked')

    def __str__(self):
        return self.student_name


# Notification Management Module
class Notification(models.Model):
    user_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class VideoSession(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )
    meeting_id = models.CharField(max_length=100)
    meeting_link = models.URLField()
    status = models.CharField(max_length=20, default="Scheduled")

    def __str__(self):
        return self.meeting_id