from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

class Skill(models.Model):
    skill_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.skill_name