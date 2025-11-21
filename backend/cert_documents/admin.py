from django.contrib import admin
from .models import CertLetter, CertLetterFile


@admin.register(CertLetter)
class CertLetterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "system",
        "number",
        "date",
        "subject",
        "performer",
        "display_dest_organizations",
        "created_at",
    )
    list_filter = (
        "system",
        "date",
        "has_deadline",
        "performer",
        "created_at",
    )
    search_fields = (
        "number",
        "subject",
        "description",
        "performer__username",
        "performer__fio",
    )
    ordering = ("-date", "-created_at")

    # показываем организации красиво
    def display_dest_organizations(self, obj):
        return ", ".join([o.name for o in obj.dest_organizations.all()])
    display_dest_organizations.short_description = "Куда отправлено"


@admin.register(CertLetterFile)
class CertLetterFileAdmin(admin.ModelAdmin):
    list_display = ("id", "letter", "original_name", "uploaded_at")
    search_fields = ("original_name",)
    ordering = ("-uploaded_at",)
