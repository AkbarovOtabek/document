from django.contrib import admin
from .models import CertDocument


@admin.register(CertDocument)
class CertDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "number",
        "date",
        "from_organization",
        "to_organization",
        "created_at",
    )
    list_filter = ("date", "from_organization",
                   "to_organization", "created_at")
    search_fields = ("title", "number", "from_organization", "to_organization")
    ordering = ("-date", "-created_at")
