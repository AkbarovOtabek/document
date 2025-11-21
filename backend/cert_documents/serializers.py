# cert_documents/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CertLetter, CertLetterFile, CertLetterReply
from organizations.models import Organization

User = get_user_model()


class CertLetterFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertLetterFile
        fields = ("id", "file", "original_name", "uploaded_at")


class CertLetterReplySerializer(serializers.ModelSerializer):
    # для красивого вывода организации
    organization_name = serializers.SerializerMethodField(read_only=True)
    organization_type_name = serializers.SerializerMethodField(read_only=True)
    added_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CertLetterReply
        fields = [
            "id",
            "letter",
            "organization",
            "organization_name",
            "organization_type_name",
            "reply_number",      # 🔹 номер ответного письма
            "internal_number",   # 🔹 внутренний номер
            "file",
            "received_date",
            "added_by",
            "added_by_name",
            "added_at",
        ]
        read_only_fields = ("added_by", "added_at")

    def get_organization_name(self, obj):
        if not obj.organization:
            return None
        return getattr(obj.organization, "name", None)

    def get_organization_type_name(self, obj):
        org = obj.organization
        if not org:
            return None
        return (
            getattr(getattr(org, "organization_type", None), "name", None)
            or getattr(getattr(org, "category", None), "name", None)
        )

    def get_added_by_name(self, obj):
        u = obj.added_by
        if not u:
            return None
        return (
            getattr(u, "full_name", None)
            or getattr(u, "fio", None)
            or f"{u.last_name} {u.first_name}".strip()
            or u.username
        )

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("added_by", request.user)
        return super().create(validated_data)


class CertLetterSerializer(serializers.ModelSerializer):
    dest_organizations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Organization.objects.all(),
        required=False
    )

    performer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    performer_name = serializers.SerializerMethodField(read_only=True)
    files = CertLetterFileSerializer(many=True, read_only=True)

    # ⬇️ ТЕПЕРЬ ОТДАЁМ ПОЛНЫЕ ОБЪЕКТЫ ОТВЕТОВ, А НЕ ТОЛЬКО ИХ ID
    replies = CertLetterReplySerializer(many=True, read_only=True)

    class Meta:
        model = CertLetter
        fields = [
            "id",
            "system",
            "number",
            "date",
            "subject",
            "performer",
            "performer_name",
            "description",
            "has_deadline",
            "deadline",
            "dest_organizations",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "files",
            "replies",
        ]
        read_only_fields = (
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def get_performer_name(self, obj):
        user = obj.performer
        if not user:
            return None

        full_name = getattr(user, "full_name", "") or getattr(user, "fio", "")
        if full_name and full_name.strip():
            return full_name.strip()

        parts = [
            getattr(user, "last_name", "") or "",
            getattr(user, "first_name", "") or "",
            getattr(user, "middle_name", "") or "",
        ]
        parts = [p.strip() for p in parts if p and p.strip()]
        if parts:
            return " ".join(parts)

        username = getattr(user, "username", "") or getattr(user, "email", "")
        return username or None

    def create(self, validated_data):
        request = self.context.get("request")

        dest_orgs = validated_data.pop("dest_organizations", [])

        if request and request.user.is_authenticated:
            validated_data.setdefault("created_by", request.user)
            validated_data.setdefault("updated_by", request.user)

        letter = CertLetter.objects.create(**validated_data)

        if dest_orgs:
            letter.dest_organizations.set(dest_orgs)

        return letter
