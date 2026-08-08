from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import PaymentViewSet, payment_page, wallet_view, add_funds, withdraw_funds, receipt_detail, my_receipts

router = SimpleRouter()
router.register(r'payments', PaymentViewSet)


urlpatterns = [
    path("pay/", payment_page, name="payment_page"),
    path("wallet/", wallet_view, name="wallet"),
    path("wallet/add/", add_funds, name="add_funds"),
    path("wallet/withdraw/", withdraw_funds, name="withdraw_funds"),
    path("receipts/", my_receipts, name="my_receipts"),
    path("receipt/<str:receipt_number>/", receipt_detail, name="receipt_detail"),
]

urlpatterns += router.urls
