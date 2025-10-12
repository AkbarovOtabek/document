# staffUsers/serializers.py
from rest_framework import serializers
from .models import StaffProfile, StaffCuratorship, ManagementUnit, Department
from organizations.models import Organization
from organizations.serializer import OrganizationSerializer


class ManagementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementUnit
        fields = ["id", "name", "slug"]


class DepartmentSerializer(serializers.ModelSerializer):
    management = ManagementUnitSerializer(read_only=True)
    management_id = serializers.PrimaryKeyRelatedField(
        source="management", queryset=ManagementUnit.objects.all(), write_only=True, required=True
    )

    class Meta:
        model = Department
        fields = ["id", "name", "slug", "management", "management_id"]


class BriefOrgSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = Organization
        fields = ["id", "slug", "name", "category_name", "category_slug", "logo"]


class StaffCuratorshipSerializer(serializers.ModelSerializer):
    staff_fio = serializers.CharField(source="staff.fio", read_only=True)
    organization_data = BriefOrgSerializer(source="organization", read_only=True)

    class Meta:
        model = StaffCuratorship
        fields = ["id", "staff", "staff_fio", "organization", "organization_data",
                  "category", "can_edit", "created_at"]
        read_only_fields = ["created_at"]


class StaffProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    fio = serializers.CharField(read_only=True)

    management = ManagementUnitSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    management_id = serializers.PrimaryKeyRelatedField(
        source="management", queryset=ManagementUnit.objects.all(), write_only=True, required=False
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source="department", queryset=Department.objects.all(), write_only=True, required=False
    )

    links = StaffCuratorshipSerializer(many=True, read_only=True, source="curator_links")

    # организации, где он куратор напрямую
    curated_organizations = BriefOrgSerializer(
        many=True, read_only=True, source="curatorships"
    )

    # организации по курируемым категориям
    curated_by_categories = serializers.SerializerMethodField()

    class Meta:
        model = StaffProfile
        fields = [
            "id", "username", "email", "fio",
            "first_name", "second_name", "last_name",
            "lotus", "work_email", "work_phone",
            "position", "role",
            "management", "department", "management_id", "department_id",
            "management_flag",
            "curated_orgs_count", "curated_cats_count",
            "curated_organizations", "curated_by_categories",
            "links",
        ]

    def get_curated_by_categories(self, obj: StaffProfile):
        from organizations.models import Organization
        cat_ids = list(obj.curator_links.filter(category__isnull=False)
                       .values_list("category_id", flat=True))
        if not cat_ids:
            return []
        qs = Organization.objects.filter(category_id__in=cat_ids).select_related("category")
        return BriefOrgSerializer(qs, many=True).data
