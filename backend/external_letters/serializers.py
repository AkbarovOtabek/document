from rest_framework import serializers
from django.utils.text import slugify
from .models import ExternalLetter, ExternalLettersCategory


def unique_slugify(model, base_slug):
    slug = slugify(base_slug) or "item"
    original = slug
    i = 1
    while model.objects.filter(slug=slug).exists():
        i += 1
        slug = f"{original}-{i}"
    return slug


class ExternalLettersCategorySerializer(serializers.ModelSerializer):
    # считать количество писем в этой категории
    objects_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ExternalLettersCategory
        fields = ["id", "name", "slug", "badge",
                  "time_create", "objects_count"]
        read_only_fields = ["id", "slug", "time_create", "objects_count"]

    def get_objects_count(self, obj):
        # related_name='letters' в модели категории
        return obj.letters.count()

    def create(self, validated_data):
        # если slug не прислали — генерируем из name
        if not validated_data.get("slug"):
            validated_data["slug"] = unique_slugify(
                ExternalLettersCategory, validated_data.get("name", "")
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # slug не трогаем при апдейте (обычно фиксируем)
        validated_data.pop("slug", None)
        return super().update(instance, validated_data)


class ExternalLetterSerializer(serializers.ModelSerializer):
    # писать будем через category_id...
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ExternalLettersCategory.objects.all(), source="category", write_only=True
    )
    # ...а читать удобно через вложенный объект
    category = ExternalLettersCategorySerializer(read_only=True)

    # файл письма
    file = serializers.FileField(required=False, allow_null=True)

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
            "time_create",
            "updated",
        ]
        read_only_fields = ["id", "slug", "time_create", "updated"]

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = unique_slugify(
                ExternalLetter, validated_data.get("title", "")
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # не даём менять slug на PATCH/PUT
        validated_data.pop("slug", None)
        return super().update(instance, validated_data)
