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


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=250.00)
    earned_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet ({self.user.username}) — ₹{self.balance}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit (Earned/Added)'),
        ('debit', 'Debit (Spent/Withdrawn)'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type.upper()} ₹{self.amount} - {self.description}"


import uuid

class PaymentReceipt(models.Model):
    """
    Payment receipt generated when a student pays for a Batch enrollment or Skill session.
    Sent to both the student and the batch teacher.
    """
    STATUS_CHOICES = [
        ('PAID', 'Paid / Completed'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Failed'),
    ]

    receipt_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    transaction_id = models.CharField(max_length=80, unique=True, blank=True, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_receipts')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_receipts')
    batch = models.ForeignKey('bookings.Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='receipts')
    item_title = models.CharField(max_length=200)
    category_name = models.CharField(max_length=100, blank=True, default='General')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='SkillBank Wallet')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PAID')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_receipts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Receipt #{self.receipt_number} — ₹{self.amount} ({self.student.username} -> {self.teacher.username})"
