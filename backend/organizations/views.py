from django.utils import timezone
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters, permissions, parsers
from .serializer import CategorySerializer, OrganizationSerializer
from .models import Category, Organization


class CategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = "slug"

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
    # permission_classes = [permissions.AllowAny]

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
