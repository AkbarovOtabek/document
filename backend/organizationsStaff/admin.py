from django.contrib import admin
from .models import OrgUnit, OrgEmployee

@admin.register(OrgUnit)
class OrgUnitAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "name", "type", "parent", "order")
    list_filter = ("organization", "type")
    search_fields = ("name", "organization__name")
    autocomplete_fields = ("organization", "parent")
    ordering = ("organization", "parent__id", "order", "name")

@admin.register(OrgEmployee)
class OrgEmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "unit", "full_name", "position_title", "is_head", "work_phone", "email", "order")
    list_filter = ("organization", "is_head")
    search_fields = ("full_name", "position_title", "organization__name", "unit__name", "email", "work_phone")
    autocomplete_fields = ("organization", "unit")
