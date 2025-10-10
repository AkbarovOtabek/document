from rest_framework.routers import DefaultRouter
from .views import StaffProfileViewSet, StaffCuratorshipViewSet

app_name = "staffUsers"

router = DefaultRouter()
router.register(r"users", StaffProfileViewSet, basename="staff-users")
router.register(r"curatorships", StaffCuratorshipViewSet,
                basename="staff-curatorships")

urlpatterns = router.urls
