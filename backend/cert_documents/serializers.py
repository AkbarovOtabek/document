from rest_framework import serializers
from .models import CertDocument


class CertDocumentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для документов CERT-CBU
    """

    class Meta:
        model = CertDocument
        fields = [
            "id",
            "title",
            "number",
            "date",
            "from_organization",
            "to_organization",
            "description",
            "file",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
