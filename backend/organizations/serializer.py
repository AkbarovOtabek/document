# organizations/serializer.py
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import serializers
from .models import Category, Organization


def unique_slugify(model, base_slug):
    slug = slugify(base_slug) or "item"
    original = slug
    i = 1
    while model.objects.filter(slug=slug).exists():
        i += 1
        slug = f"{original}-{i}"
    return slug


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    objects_count = serializers.IntegerField(read_only=True)
    today_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'badge', 'time_create',
                  'objects_count', 'today_count']
        read_only_fields = ['slug', 'time_create',
                            'objects_count', 'today_count']

    def create(self, validated_data):
        validated_data['slug'] = unique_slugify(
            Category, validated_data.get('name', ''))
        return super().create(validated_data)


class OrganizationSerializer(serializers.ModelSerializer):
    # read-only про категорию
    category_name = serializers.CharField(
        source="category.name", read_only=True)
    category_slug = serializers.CharField(
        source="category.slug", read_only=True)

    # опционально — создать/обновить по slug категории
    category_slug_in = serializers.SlugField(write_only=True, required=False)

    # slug организации только читаем
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id", "slug", "name", "description", "address", "lotus", "phone", "email",
            "category",           # id категории (write)
            "category_name",      # name (read)
            "category_slug",      # slug (read)
            "category_slug_in",   # slug (write)
            "logo", "time_create", "updated",
        ]
        read_only_fields = ["slug", "time_create", "updated"]

    def validate(self, attrs):
        # если прислали category_slug_in — подменим category
        slug_in = attrs.pop("category_slug_in", None)
        if slug_in and not attrs.get("category"):
            try:
                attrs["category"] = Category.objects.get(slug=slug_in)
            except Category.DoesNotExist:
                raise serializers.ValidationError(
                    {"category_slug_in": "Категория с таким slug не найдена"})
        return attrs

    def create(self, validated_data):
        validated_data["slug"] = unique_slugify(
            Organization, validated_data.get("name", ""))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # если меняем name — можно (опционально) пересоздавать slug
        if "name" in validated_data and validated_data["name"] and validated_data["name"] != instance.name:
            validated_data["slug"] = unique_slugify(
                Organization, validated_data["name"])
        return super().update(instance, validated_data)
