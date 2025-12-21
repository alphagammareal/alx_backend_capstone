from rest_framework.routers import DefaultRouter
from .views import InvestmentViewSet

router = DefaultRouter()
router.register("portfolio", InvestmentViewSet, basename="portfolio")

urlpatterns = router.urls
