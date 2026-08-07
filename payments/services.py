import uuid


class PaymentService:

    @staticmethod
    def generate_transaction_id():
        return "TXN-" + str(uuid.uuid4())[:8].upper()

    @staticmethod
    def process_payment(amount):
        """
        Simulated payment gateway.
        """

        if amount <= 0:
            return {
                "success": False,
                "message": "Invalid payment amount"
            }

        return {
            "success": True,
            "transaction_id": PaymentService.generate_transaction_id(),
            "status": "Success"
        }