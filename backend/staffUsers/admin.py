from django.contrib import admin
from .models import StaffProfile, StaffCuratorship, AuditEntry


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "fio", "role", "phone",
                    "management", "curated_orgs_count", "curated_cats_count")
    list_filter = ("role", "management")
    search_fields = ("user__username", "last_name",
                     "first_name", "second_name", "phone")


@admin.register(StaffCuratorship)
class StaffCuratorshipAdmin(admin.ModelAdmin):
    list_display = ("id", "staff", "organization",
                    "category", "can_edit", "created_at")
    list_filter = ("can_edit", "category")
    search_fields = ("staff__user__username",
                     "organization__name", "category__name")


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("created", "actor", "target", "org", "category", "action")
    list_filter = ("target", "action", "created")
    autocomplete_fields = ("actor", "org", "category")
