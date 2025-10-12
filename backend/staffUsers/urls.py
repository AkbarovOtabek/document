from rest_framework.routers import DefaultRouter
from .views import StaffProfileViewSet, StaffCuratorshipViewSet,ManagementUnitViewSet, DepartmentViewSet

app_name = "staffUsers"
router = DefaultRouter()

router.register(r"users", StaffProfileViewSet, basename="staff-users")
router.register(r"curatorships", StaffCuratorshipViewSet, basename="staff-curatorships")
router.register(r"management", ManagementUnitViewSet, basename="management")
router.register(r"departments", DepartmentViewSet, basename="departments")

urlpatterns = router.urls
