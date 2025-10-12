from django.utils import timezone
from django.db.models import Count, Q,Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializer import CategorySerializer, OrganizationSerializer
from .models import Category, Organization

from staffUsers.permissions import IsStaffOrReadOnly, CanEditCategory, CanEditOrganization
from staffUsers.models import AuditEntry, StaffProfile,StaffCuratorship

from organizationsStaff.models import OrgUnit
from organizationsStaff.serializers import OrgUnitTreeSerializer


# class OrganizationViewSet(viewsets.ModelViewSet):
#     # ... как у вас уже есть ...

#     @action(detail=True, methods=["get"], url_path="structure")
#     def structure(self, request, *args, **kwargs):
#         org = self.get_object()
#         qs = (
#             OrgUnit.objects
#             .filter(organization=org, parent__isnull=True)
#             .prefetch_related(
#                 "children",
#                 "children__children",        # слегка хелпит, но глубина может быть произвольной
#                 "employees",
#             )
#             .order_by("order", "name")
#         )
#         data = OrgUnitTreeSerializer(qs, many=True, context={"request": request}).data
#         return Response({"organization": org.slug, "units": data})



class CategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = "slug"
    permission_classes = [IsStaffOrReadOnly & CanEditCategory]

    def perform_create(self, serializer):
        obj = serializer.save()
        staff = getattr(self.request.user, "staff", None)
        AuditEntry.objects.create(
            actor=staff, target=AuditEntry.Target.CAT, category=obj, action="created")

    def perform_update(self, serializer):
        obj = serializer.save()
        staff = getattr(self.request.user, "staff", None)
        AuditEntry.objects.create(
            actor=staff, target=AuditEntry.Target.CAT, category=obj, action="updated")

    def perform_destroy(self, instance):
        staff = getattr(self.request.user, "staff", None)
        AuditEntry.objects.create(
            actor=staff, target=AuditEntry.Target.CAT, category=instance, action="deleted")
        return super().perform_destroy(instance)

    def get_queryset(self):
        today = timezone.localdate()
        return (
            Category.objects
            .annotate(
                objects_count=Count('organizations'),
                today_count=Count('organizations', filter=Q(
                    organizations__time_create__date=today))
            )
            .order_by('name')
        )

# если нужно — аналогичный ViewSet для организаций:


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("category").all()
    serializer_class = OrganizationSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    permission_classes = [IsStaffOrReadOnly & CanEditOrganization]

    parser_classes = [parsers.MultiPartParser,
                      parsers.FormParser, parsers.JSONParser]

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    # /orgs/?category=1 или ?category__slug=banki
    filterset_fields = ["category", "category__slug"]
    search_fields = ["name", "description",
                     "address", "lotus", "phone", "email"]
    ordering_fields = ["time_create", "updated", "name"]
    ordering = ["-time_create"]

    def get_queryset(self):
        org_links_qs = (
            StaffCuratorship.objects
            .select_related("staff", "staff__user")     # чтобы были fio/phone/username
            .filter(organization__isnull=False)
        )
        cat_links_qs = (
            StaffCuratorship.objects
            .select_related("staff", "staff__user")
            .filter(category__isnull=False)
        )
        return (
            Organization.objects
            .select_related("category")
            .prefetch_related(
                Prefetch("curator_links", queryset=org_links_qs, to_attr="curator_links_all_org"),
                Prefetch("category__curator_links", queryset=cat_links_qs, to_attr="curator_links_all_cat"),
            )
        )

    @action(detail=True, methods=["get"], url_path="structure")
    def structure(self, request, *args, **kwargs):
        org = self.get_object()
        roots = (OrgUnit.objects
                 .filter(organization=org, parent__isnull=True)
                 .prefetch_related("children", "children__children", "employees")
                 .order_by("order", "name"))
        data = OrgUnitTreeSerializer(roots, many=True, context={"request": request}).data
        return Response({"organization": org.slug, "units": data})


    def perform_create(self, serializer):
        obj = serializer.save()
        staff = getattr(self.request.user, "staff", None)
        AuditEntry.objects.create(
            actor=staff, target=AuditEntry.Target.ORG, org=obj, action="created")

    def perform_update(self, serializer):
        obj = serializer.save()
        staff = getattr(self.request.user, "staff", None)
        AuditEntry.objects.create(
            actor=staff, target=AuditEntry.Target.ORG, org=obj, action="updated")

    def perform_destroy(self, instance):
        staff = getattr(self.request.user, "staff", None)
        AuditEntry.objects.create(
            actor=staff, target=AuditEntry.Target.ORG, org=instance, action="deleted")
        return super().perform_destroy(instance)
