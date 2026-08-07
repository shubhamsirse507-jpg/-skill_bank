from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Earning
from .serializers import EarningSerializer
from .services import EarningsService


class EarningViewSet(viewsets.ModelViewSet):

    queryset = Earning.objects.all()
    serializer_class = EarningSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        total_amount = serializer.validated_data["total_amount"]

        result = EarningsService.calculate(total_amount)

        serializer.save(
            commission=result["commission"],
            teacher_earning=result["teacher_earning"]
        )

        