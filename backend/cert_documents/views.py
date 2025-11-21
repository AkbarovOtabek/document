# cert_documents/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import CertLetter, CertLetterFile, CertLetterReply
from .serializers import (
    CertLetterSerializer,
    CertLetterFileSerializer,
    CertLetterReplySerializer,
)
from .filters import CertLetterFilter


class CertLetterViewSet(viewsets.ModelViewSet):
    queryset = (
        CertLetter.objects
        .all()
        .select_related("performer", "created_by", "updated_by")
        .prefetch_related("dest_organizations", "files", "replies")
    )
    serializer_class = CertLetterSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # Фильтрация / поиск / сортировка
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CertLetterFilter

    search_fields = [
        "number",
        "subject",
        "description",
    ]

    ordering_fields = [
        "date",
        "deadline",
        "created_at",
        "updated_at",
    ]
    ordering = ["-date", "-id"]

    def perform_create(self, serializer):
        # created_by / updated_by ставятся в serializer.create
        letter = serializer.save()

        # файлы из формы (files)
        for f in self.request.FILES.getlist("files"):
            CertLetterFile.objects.create(
                letter=letter,
                file=f,
                original_name=getattr(f, "name", ""),
            )


class CertLetterReplyViewSet(viewsets.ModelViewSet):
    """
    CRUD для ответных писем.
    POST multipart/form-data:
      - letter (id CertLetter)
      - organization (id Organization)
      - received_date (YYYY-MM-DD)
      - file (файл)
    """
    queryset = (
        CertLetterReply.objects
        .all()
        .select_related("letter", "organization", "added_by")
    )
    serializer_class = CertLetterReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # added_by устанавливается в serializer.create
        serializer.save()
