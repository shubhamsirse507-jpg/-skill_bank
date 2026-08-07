from django.shortcuts import render
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

