from decimal import Decimal


class EarningsService:

    PLATFORM_COMMISSION = Decimal("0.10")

    @staticmethod
    def calculate(total_amount):

        commission = total_amount * EarningsService.PLATFORM_COMMISSION

        teacher_amount = total_amount - commission

        return {
            "commission": commission,
            "teacher_earning": teacher_amount,
        }