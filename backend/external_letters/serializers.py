from rest_framework import serializers
from django.utils.text import slugify
from .models import ExternalLetter, ExternalLettersCategory, ExternalLetterReply


def unique_slugify(model, base_slug):
    slug = slugify(base_slug) or "item"
    original = slug
    i = 1
    while model.objects.filter(slug=slug).exists():
        i += 1
        slug = f"{original}-{i}"
    return slug


class ExternalLettersCategorySerializer(serializers.ModelSerializer):
    # количество писем в категории
    objects_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ExternalLettersCategory
        fields = ["id", "name", "slug", "badge",
                  "time_create", "objects_count"]
        read_only_fields = ["id", "slug", "time_create", "objects_count"]

    def get_objects_count(self, obj):
        return obj.letters.count()

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = unique_slugify(
                ExternalLettersCategory, validated_data.get("name", "")
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("slug", None)
        return super().update(instance, validated_data)


class ExternalLetterReplySerializer(serializers.ModelSerializer):
    # для записи используем letter_id, для чтения достаточно pk письма
    letter_id = serializers.PrimaryKeyRelatedField(
        queryset=ExternalLetter.objects.all(),
        source="letter",
        write_only=True,
    )
    letter = serializers.PrimaryKeyRelatedField(read_only=True)

    added_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ExternalLetterReply
        fields = [
            "id",
            "letter",
            "letter_id",
            "reply_number",
            "internal_number",
            "sent_date",
            "file",
            "added_by",
            "added_by_name",
            "added_at",
        ]
        read_only_fields = ["added_by", "added_at"]

    def get_added_by_name(self, obj):
        u = obj.added_by
        if not u:
            return None
        return u.get_full_name() or u.username

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["added_by"] = request.user
        return super().create(validated_data)


class ExternalLetterSerializer(serializers.ModelSerializer):
    # писать будем через category_id...
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ExternalLettersCategory.objects.all(),
        source="category",
        write_only=True,
    )
    # ...а читать — через вложенную категорию
    category = ExternalLettersCategorySerializer(read_only=True)

    file = serializers.FileField(required=False, allow_null=True)
    registration_date = serializers.DateField(required=False, allow_null=True)
    incoming_date = serializers.DateField(required=False, allow_null=True)

    # вложенный список ответных писем
    replies = ExternalLetterReplySerializer(many=True, read_only=True)

    class Meta:
        model = ExternalLetter
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "letter_number",
            "internal_letter_number",
            "executor",
            "category",
            "category_id",
            "file",
            "registration_date",
            "incoming_date",
            "time_create",
            "updated",
            "replies",  # <<< важно
        ]
        read_only_fields = ["id", "slug", "time_create", "updated"]

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = unique_slugify(
                ExternalLetter, validated_data.get("title", "")
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("slug", None)
        return super().update(instance, validated_data)
