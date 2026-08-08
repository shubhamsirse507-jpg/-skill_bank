from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Payment
from .serializers import PaymentSerializer
from .services import PaymentService


class PaymentViewSet(viewsets.ModelViewSet):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        payment_result = PaymentService.process_payment(
            serializer.validated_data["amount"]
        )

        if not payment_result["success"]:
            return Response(
                payment_result,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(
            transaction_id=payment_result["transaction_id"],
            payment_status=payment_result["status"]
        )

        return Response(
            {
                "message": "Payment Successful",
                "transaction_id": payment_result["transaction_id"]
            },
            status=status.HTTP_201_CREATED
        )


# This function must be OUTSIDE the class
def payment_page(request):
    return render(request, "payments/payment.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import Wallet, WalletTransaction
from decimal import Decimal


@login_required
def wallet_view(request):
    """SkillBank Wallet view matching Lovable app."""
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()
    return render(request, "payments/wallet.html", {
        "wallet": wallet,
        "transactions": transactions,
    })


@login_required
def add_funds(request):
    """Adds funds/credits to SkillBank wallet."""
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount", "0"))
            method = request.POST.get("payment_method", "UPI")
            if amount > 0:
                wallet, _ = Wallet.objects.get_or_create(user=request.user)
                wallet.balance = Decimal(str(wallet.balance)) + amount
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type="credit",
                    description=f"Added funds via {method}"
                )
                messages.success(request, f"Successfully added ₹{amount} to your SkillBank wallet!")
            else:
                messages.error(request, "Please enter a valid positive amount.")
        except Exception as e:
            messages.error(request, f"Transaction error: {str(e)}")

    return redirect("wallet")


@login_required
def withdraw_funds(request):
    """Withdraws earnings from SkillBank wallet."""
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount", "0"))
            upi_id = request.POST.get("upi_id", "").strip()
            wallet, _ = Wallet.objects.get_or_create(user=request.user)

            if amount > 0 and amount <= wallet.balance:
                wallet.balance -= amount
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type="debit",
                    description=f"Payout withdrawal to {upi_id or 'Bank Account'}"
                )
                messages.success(request, f"Payout of ₹{amount} initiated to {upi_id or 'your bank account'}!")
            else:
                messages.error(request, "Insufficient balance or invalid amount.")
        except Exception as e:
            messages.error(request, f"Withdrawal error: {str(e)}")

    return redirect("wallet")


from .models import PaymentReceipt


@login_required
def receipt_detail(request, receipt_number):
    """
    Renders official Payment Receipt for a batch enrollment or session.
    Accessible by student (payer), teacher (payee), or admin.
    """
    receipt = get_object_or_404(
        PaymentReceipt.objects.select_related('student', 'teacher', 'batch'),
        receipt_number=receipt_number
    )

    if not (request.user == receipt.student or request.user == receipt.teacher or request.user.is_staff):
        messages.error(request, "You do not have permission to view this payment receipt.")
        return redirect('my_receipts')

    return render(request, 'payments/receipt_detail.html', {
        'receipt': receipt,
    })


@login_required
def my_receipts(request):
    """
    Lists all payment receipts for current user:
    - Sent payments (as student)
    - Received payments (as batch teacher)
    Auto-backfills receipts for existing BatchEnrollments if missing.
    """
    from bookings.models import BatchEnrollment, Batch
    import uuid

    # 1. Backfill student enrollments if receipt missing
    student_enrollments = BatchEnrollment.objects.filter(student=request.user).select_related('batch', 'batch__instructor', 'batch__category')
    for enrollment in student_enrollments:
        if enrollment.batch and not PaymentReceipt.objects.filter(student=request.user, batch=enrollment.batch).exists():
            tx_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
            PaymentReceipt.objects.create(
                student=request.user,
                teacher=enrollment.batch.instructor,
                batch=enrollment.batch,
                item_title=enrollment.batch.title,
                category_name=enrollment.batch.category.category_name if enrollment.batch.category else 'General',
                amount=enrollment.batch.price_credits,
                payment_method='SkillBank Wallet',
                transaction_id=tx_id,
                status='PAID'
            )

    # 2. Backfill teacher batch enrollments if receipt missing
    teacher_batches = Batch.objects.filter(instructor=request.user).prefetch_related('enrollments__student', 'category')
    for b in teacher_batches:
        for enr in b.enrollments.all():
            if not PaymentReceipt.objects.filter(student=enr.student, batch=b).exists():
                tx_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
                PaymentReceipt.objects.create(
                    student=enr.student,
                    teacher=request.user,
                    batch=b,
                    item_title=b.title,
                    category_name=b.category.category_name if b.category else 'General',
                    amount=b.price_credits,
                    payment_method='SkillBank Wallet',
                    transaction_id=tx_id,
                    status='PAID'
                )

    sent_receipts = PaymentReceipt.objects.filter(student=request.user).select_related('teacher', 'batch')
    received_receipts = PaymentReceipt.objects.filter(teacher=request.user).select_related('student', 'batch')

    return render(request, 'payments/receipt_list.html', {
        'sent_receipts': sent_receipts,
        'received_receipts': received_receipts,
    })



