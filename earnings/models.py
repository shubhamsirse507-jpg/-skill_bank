from django.db import models
from django.contrib.auth import get_user_model
from payments.models import Payment

User = get_user_model()


class Earning(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
    ]

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="earning"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_earnings"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    commission = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    teacher_earning = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.teacher.username} - ₹{self.teacher_earning}"