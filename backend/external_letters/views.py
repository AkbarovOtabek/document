from .models import ExternalLetter, ExternalLettersCategory, ExternalLetterReply
from .serializers import (
    ExternalLetterSerializer,
    ExternalLettersCategorySerializer,
    ExternalLetterReplySerializer,
)
from rest_framework import viewsets, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class ExternalLettersCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ExternalLettersCategory.objects.all().order_by("name")
    serializer_class = ExternalLettersCategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "time_create"]


class ExternalLetterViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        ExternalLetter.objects
        .select_related("category")
        .prefetch_related("replies", "replies__added_by")
        .all()
        .order_by("-time_create")
    )
    serializer_class = ExternalLetterSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "category__slug": ["exact"],          # NQQ / MBQ / ...
        "registration_date": ["gte", "lte"],  # от / до даты регистрации
        "letter_number": ["exact", "icontains"],
        "executor": ["icontains"],
        "title": ["icontains"],
        "description": ["icontains"],
    }
    search_fields = [
        "title",
        "description",
        "letter_number",
        "internal_letter_number",
        "executor",
        "category__name",
    ]
    ordering_fields = ["time_create", "updated", "title"]


class ExternalLetterReplyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ExternalLetterReply.objects.select_related(
        "letter", "added_by").all()
    serializer_class = ExternalLetterReplySerializer
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "letter__id": ["exact"],
        "reply_number": ["icontains"],
        "internal_number": ["icontains"],
        "sent_date": ["gte", "lte"],
    }
    search_fields = [
        "reply_number",
        "internal_number",
        "letter__title",
        "letter__letter_number",
    ]
    ordering_fields = ["sent_date", "added_at"]
