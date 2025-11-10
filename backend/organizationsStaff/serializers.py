
from rest_framework import serializers
from .models import OrgUnit, OrgEmployee


class OrgEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgEmployee
        fields = [
            "id", "full_name", "position_title",
            "work_phone", "email", "lotus",
            "is_head", "order",
            "unit", "organization", "created_at",
        ]
        read_only_fields = ["created_at"]


class OrgEmployeeBriefSerializer(serializers.ModelSerializer):
    fio = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    position_display = serializers.SerializerMethodField()

    class Meta:
        model = OrgEmployee
        fields = ["id", "fio", "phone", "email", "position_display", "is_head"]

    def get_fio(self, obj): return obj.full_name
    def get_phone(self, obj): return obj.work_phone
    def get_position_display(self, obj): return obj.position_title or ""


class OrgUnitTreeSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = OrgUnit
        fields = [
            "id",
            "name",
            "type",
            "parent_id",
            "children",
        ]

    def get_parent_id(self, obj):
        return getattr(obj, "parent_id", None)

    def get_children(self, obj):
        # защита от зацикливания + лимит глубины
        ctx = self.context
        visited = ctx.setdefault("visited", set())
        max_depth = ctx.get("max_depth", 20)
        depth = ctx.setdefault("_depth", 0)

        if obj.pk in visited or depth >= max_depth:
            return []

        visited.add(obj.pk)
        try:
            ctx["_depth"] = depth + 1
            # thanks to related_name="children"
            qs = obj.children.all().order_by("order", "name")
            return OrgUnitTreeSerializer(qs, many=True, context=ctx).data
        finally:
            ctx["_depth"] = depth


class OrgUnitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgUnit
        fields = [
            "id", "organization", "parent", "name", "type", "order"
        ]


class OrgUnitFlatSerializer(serializers.ModelSerializer):
    parent_id = serializers.SerializerMethodField()

    class Meta:
        model = OrgUnit
        fields = [
            "id",
            "organization",    # это будет ID организации
            "name",
            "type",            # одна из: directorate/management/department/section/other
            "parent_id",       # только ID родителя
        ]

    def get_parent_id(self, obj):
        return getattr(obj, "parent_id", None)
