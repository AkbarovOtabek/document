
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
    employees = OrgEmployeeBriefSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = OrgUnit
        fields = ["id", "name", "type", "order", "children", "employees"]

    def get_children(self, obj):
        kids = obj.children.all().order_by("order", "name")
        return OrgUnitTreeSerializer(kids, many=True, context=self.context).data


class OrgUnitWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgUnit
        fields = [
            "id", "organization", "parent", "name", "type", "order"
        ]
