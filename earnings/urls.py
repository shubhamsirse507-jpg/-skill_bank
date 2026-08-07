from rest_framework.routers import DefaultRouter
from .views import EarningViewSet

router = DefaultRouter()
router.register(r'earnings', EarningViewSet)

urlpatterns = router.urls