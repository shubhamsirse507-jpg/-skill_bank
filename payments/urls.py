from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, payment_page

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path("pay/", payment_page, name="payment_page"),
]

urlpatterns += router.urls