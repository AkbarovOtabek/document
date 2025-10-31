from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from .models import Category, Organization
from organizationsStaff.models import OrgUnit
from organizationsStaff.serializers import OrgUnitTreeSerializer
from staffUsers.models import StaffProfile, StaffCuratorship
from django.db import transaction
User = get_user_model()


def unique_slugify(model, base_slug):
    slug = slugify(base_slug) or "item"
    original = slug
    i = 1
    while model.objects.filter(slug=slug).exists():
        i += 1
        slug = f"{original}-{i}"
    return slug


class StaffBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="staff.id", read_only=True)
    username = serializers.CharField(
        source="staff.user.username", read_only=True)
    fio = serializers.CharField(source="staff.fio", read_only=True)
    phone = serializers.CharField(source="staff.phone", read_only=True)
    role = serializers.CharField(source="staff.role", read_only=True)
    management = serializers.BooleanField(
        source="staff.management", read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    # "organization" | "category"
    source = serializers.CharField(read_only=True)


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


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class OrganizationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True)
    category_slug = serializers.CharField(
        source="category.slug", read_only=True)
    category_slug_in = serializers.SlugField(write_only=True, required=False)

    curator = serializers.IntegerField(
        write_only=True, required=False, allow_null=True)
    # curator_data = UserMiniSerializer(source="curator", read_only=True)

    # slug организации только читаем
    slug = serializers.SlugField(read_only=True)
    units_tree = serializers.SerializerMethodField()
    responsibles = serializers.SerializerMethodField()
    # primary_responsible = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id", "slug", "name", "description", "address", "lotus", "phone", "email",
            "category", "category_name", "category_slug", "category_slug_in", "logo",
            "time_create", "updated", "responsibles", "units_tree", "curator",
            # "structure",
        ]
        read_only_fields = ["slug", "time_create", "updated"]

    def get_units_tree(self, obj):
        roots = (
            OrgUnit.objects
            .filter(organization=obj, parent__isnull=True)
            .prefetch_related("children", "employees")
            .order_by("order", "name")
        )
        return OrgUnitTreeSerializer(roots, many=True).data

    def _apply_curator(self, org: Organization, curator_id):
        """
        Обновляем связь куратор↔организация:
        - если curator_id = None/"" → удаляем существующие связи
        - если передан id → оставляем только его (can_edit=True)
        """
        # очищаем текущие связи куратора с этой организацией
        StaffCuratorship.objects.filter(organization=org).delete()

        if curator_id:
            staff = StaffProfile.objects.get(pk=int(curator_id))
            StaffCuratorship.objects.create(
                staff=staff, organization=org, can_edit=True
            )

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

    @transaction.atomic
    def create(self, validated_data):
        # возьмём, если DRF положил сюда
        curator_id = validated_data.pop("curator", None)
        # если фронт шлёт FormData, DRF может не положить в validated_data — возьмём из initial_data
        if curator_id is None:
            curator_id = self.initial_data.get("curator")

        validated_data["slug"] = unique_slugify(
            Organization, validated_data.get("name", ""))
        org = super().create(validated_data)

        # применим куратора
        if curator_id is not None:
            self._apply_curator(org, curator_id)
        return org

    @transaction.atomic
    def update(self, instance, validated_data):
        curator_id = validated_data.pop("curator", None)
        if curator_id is None and "curator" in self.initial_data:
            curator_id = self.initial_data.get("curator")

        # обновим слаг при смене имени (как было)
        if "name" in validated_data and validated_data["name"] and validated_data["name"] != instance.name:
            validated_data["slug"] = unique_slugify(
                Organization, validated_data["name"])

        org = super().update(instance, validated_data)

        # если фронт прислал curator — применяем (в т.ч. очистку)
        if "curator" in (self.initial_data or {}):
            self._apply_curator(org, curator_id)
        return org

    def _map_link(self, link, source: str):
        # превращаем объект StaffCuratorship в dict, который поймёт StaffBriefSerializer
        return {"staff": link.staff, "can_edit": link.can_edit, "source": source}

    def get_responsibles(self, obj: Organization):
        org_links = getattr(obj, "curator_links_all_org",
                            None) or obj.curator_links.all()
        cat_links = getattr(obj, "curator_links_all_cat",
                            None) or obj.category.curator_links.all()
        data = [self._map_link(l, "organization") for l in org_links] + \
               [self._map_link(l, "category") for l in cat_links]
        return StaffBriefSerializer(data, many=True).data
