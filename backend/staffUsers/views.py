from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StaffProfile, StaffCuratorship
from .serializers import StaffProfileSerializer, StaffCuratorshipSerializer


class StaffProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD сотрудников (профили).
    GET /api/staff/users/
    """
    queryset = StaffProfile.objects.select_related("user").all()
    serializer_class = StaffProfileSerializer
    # управлять профилями — только админам (можете ослабить)
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Вернёт профиль текущего авторизованного пользователя."""
        try:
            profile = request.user.staff
        except Exception:
            return Response({"detail": "Not a staff user"}, status=403)
        return Response(self.get_serializer(profile).data)


class StaffCuratorshipViewSet(viewsets.ModelViewSet):
    """
    CRUD связей кураторств.
    """
    queryset = StaffCuratorship.objects.select_related(
        "staff", "organization", "category")
    serializer_class = StaffCuratorshipSerializer
    # управлять связями — только админам/менеджерам
    permission_classes = [permissions.IsAdminUser]
