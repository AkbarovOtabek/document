from rest_framework.routers import DefaultRouter
from .views import OrgUnitViewSet, OrgEmployeeViewSet

app_name = "organizationsStaff"
router = DefaultRouter()
router.register(r"units", OrgUnitViewSet, basename="org-units")
router.register(r"employees", OrgEmployeeViewSet, basename="org-employees")
urlpatterns = router.urls
