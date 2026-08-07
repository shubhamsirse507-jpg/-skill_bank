from rest_framework import serializers
from .models import Earning


class EarningSerializer(serializers.ModelSerializer):

    class Meta:
        model = Earning
        fields = "__all__"

    def validate_total_amount(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )

        return value