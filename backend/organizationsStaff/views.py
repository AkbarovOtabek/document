from rest_framework import viewsets, permissions
from rest_framework.response import Response
from staffUsers.permissions import IsStaffOrReadOnly, CanEditOrgObject
from .models import OrgUnit, OrgEmployee
from .serializers import *
from rest_framework.decorators import action


class OrgUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrgUnit.objects.all()
    serializer_class = OrgUnitFlatSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        org_id = self.request.query_params.get(
            "organization_id") or self.request.query_params.get("organization")
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return qs.select_related("parent", "organization")

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request, *args, **kwargs):
        org_id = request.query_params.get(
            "organization_id") or request.query_params.get("organization")
        roots = self.get_queryset().filter(parent__isnull=True)
        if org_id:
            roots = roots.filter(organization_id=org_id)

        # подтягиваем детей заранее, если есть related_name='children'
        roots = roots.prefetch_related("children")

        ser = OrgUnitTreeSerializer(roots, many=True, context={
                                    "visited": set(), "max_depth": 20})
        return Response(ser.data)


class OrgEmployeeViewSet(viewsets.ModelViewSet):
    queryset = OrgEmployee.objects.select_related("organization", "unit")
    serializer_class = OrgEmployeeSerializer
    # permission_classes = [IsStaffOrReadOnly, CanEditOrgObject]

    # def get_permissions(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated(), IsStaffOrReadOnly()]
