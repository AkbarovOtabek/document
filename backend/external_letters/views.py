from django.shortcuts import render
from .models import ExternalLetter, ExternalLettersCategory
from .serializers import ExternalLetterSerializer, ExternalLettersCategorySerializer
from rest_framework import viewsets, mixins, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class ExternalLettersCategoryViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = ExternalLettersCategory.objects.all().order_by('name')
    serializer_class = ExternalLettersCategorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = "slug"
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'time_create']


class ExternalLetterViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = ExternalLetter.objects.select_related(
        "category").all().order_by('-time_create')
    serializer_class = ExternalLetterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = "slug"
    parser_classes = [MultiPartParser, FormParser]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug']       # ? добавь ещё при нужде
    search_fields = ['title', 'description', 'letter_number',
                     'internal_letter_number', 'executor', 'category__name']
    ordering_fields = ['time_create', 'updated', 'title']
