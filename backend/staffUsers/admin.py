# staffUsers/admin.py
from django.contrib import admin
from .models import StaffProfile, StaffCuratorship, AuditEntry, ManagementUnit, Department


@admin.register(ManagementUnit)
class ManagementUnitAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "management")
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ("management",)
    search_fields = ("name", "management__name")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "fio", "position", "role",
                    "work_phone", "work_email", "management", "department",
                    "curated_orgs_count", "curated_cats_count")
    list_filter = ("position", "role", "management", "department")
    search_fields = ("user__username", "last_name", "first_name", "second_name", "work_phone", "work_email")


@admin.register(StaffCuratorship)
class StaffCuratorshipAdmin(admin.ModelAdmin):
    list_display = ("id", "staff", "organization", "category", "can_edit", "created_at")
    list_filter = ("can_edit", "category")
    search_fields = ("staff__user__username", "organization__name", "category__name")


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("created", "actor", "target", "org", "category", "action")
    list_filter = ("target", "action", "created")
    autocomplete_fields = ("actor", "org", "category")
