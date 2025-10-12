from rest_framework import viewsets, permissions
from staffUsers.permissions import IsStaffOrReadOnly, CanEditOrgObject
from .models import OrgUnit, OrgEmployee
from .serializers import OrgUnitTreeSerializer, OrgEmployeeSerializer

class OrgUnitViewSet(viewsets.ModelViewSet):
    queryset = OrgUnit.objects.select_related("organization", "parent").prefetch_related("children", "employees")
    serializer_class = OrgUnitTreeSerializer
    permission_classes = [IsStaffOrReadOnly, CanEditOrgObject]

    # def get_permissions(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated(), IsStaffOrReadOnly()]

    # def perform_create(self, serializer):
    #     unit = serializer.save()
    #     # тут можно логировать или проверять curator’ов

class OrgEmployeeViewSet(viewsets.ModelViewSet):
    queryset = OrgEmployee.objects.select_related("organization", "unit")
    serializer_class = OrgEmployeeSerializer
    permission_classes = [IsStaffOrReadOnly,CanEditOrgObject]

    # def get_permissions(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated(), IsStaffOrReadOnly()]
