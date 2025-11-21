# Statistics_site/urls.py
from rest_framework.routers import DefaultRouter
from .views import CertStatisticsViewSet

router = DefaultRouter()
router.register("cert", CertStatisticsViewSet, basename="cert-statistics")

urlpatterns = router.urls
