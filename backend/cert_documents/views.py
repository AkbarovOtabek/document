from rest_framework import viewsets, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import CertDocument
from .serializers import CertDocumentSerializer


class CertDocumentViewSet(viewsets.ModelViewSet):
    """
    CRUD для документов CERT-CBU

    Поддерживает:
    - список / фильтрацию / поиск
    - создание (с загрузкой файла)
    - обновление
    - удаление
    """

    queryset = CertDocument.objects.all()
    serializer_class = CertDocumentSerializer

    # чтобы принимать файл + форму
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # фильтрация и поиск
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["date", "from_organization",
                        "to_organization", "number"]
    search_fields = ["title", "description", "number",
                     "from_organization", "to_organization"]
    ordering_fields = ["date", "created_at"]
    ordering = ["-date", "-created_at"]
