from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Payment(models.Model):

    PAYMENT_METHOD = (
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('NET_BANKING', 'Net Banking'),
    )

    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    )

    learner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="learner_payment"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_payment"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD
    )

    transaction_id = models.CharField(
    max_length=50,
    unique=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.transaction_id)