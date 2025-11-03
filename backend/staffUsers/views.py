from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StaffProfile, StaffCuratorship, ManagementUnit, Department, Center

from .serializers import StaffProfileSerializer, StaffCuratorshipSerializer, ManagementUnitSerializer, DepartmentSerializer, CenterSerializer


class CenterViewSet(viewsets.ModelViewSet):
    queryset = Center.objects.all().order_by("name")
    serializer_class = CenterSerializer
    # permission_classes = [permissions.IsAdminUser]  # при желании ослабьте


class ManagementUnitViewSet(viewsets.ModelViewSet):
    queryset = ManagementUnit.objects.all().order_by("name")
    serializer_class = ManagementUnitSerializer
    # при желании ослабьте до IsAuthenticated/ReadOnly
    permission_classes = [permissions.IsAdminUser]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related("management").all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAdminUser]


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related("user").all()
    serializer_class = StaffProfileSerializer
    # управлять профилями — только админам (можете ослабить)
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            profile = request.user.staff
        except Exception:
            return Response({"detail": "Not a staff user"}, status=403)
        return Response(self.get_serializer(profile).data)


class StaffCuratorshipViewSet(viewsets.ModelViewSet):
    queryset = StaffCuratorship.objects.select_related(
        "staff", "organization", "category")
    serializer_class = StaffCuratorshipSerializer
    # управлять связями — только админам/менеджерам
    permission_classes = [permissions.IsAdminUser]
