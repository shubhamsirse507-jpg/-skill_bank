from django.db import models

class Dashboard(models.Model):
    user_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile/', blank=True, null=True)
    skills = models.TextField()
    notifications = models.IntegerField(default=0)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_name