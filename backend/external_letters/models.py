from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid
import os


def letter_upload_to(instance, filename: str) -> str:
    """
    media/external_letters/<category_slug>/<year>/<uuid>_<orig.ext>
    """
    cat = instance.category.slug if instance.category_id else "uncategorized"
    year = instance.time_create.year if instance.pk else timezone.now().year
    base, ext = os.path.splitext(filename)
    return f"external_letters/{cat}/{year}/{uuid.uuid4().hex}{ext.lower()}"


class ExternalLettersCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    badge = models.CharField(max_length=50, blank=True, default="")
    time_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Категория письма"
        verbose_name_plural = "Категории писем"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:120]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ExternalLetter(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, default="")

    # номера: внешний и внутренний
    letter_number = models.CharField(
        "Входящий/Исходящий №", max_length=100, blank=True, default="")
    internal_letter_number = models.CharField(
        "Внутренний №", max_length=100, blank=True, default="")

    executor = models.CharField(max_length=200, blank=True, default="")

    category = models.ForeignKey(
        ExternalLettersCategory,
        related_name="letters",
        on_delete=models.PROTECT,          # PROTECT, чтобы не удалить категорию с письмами
    )

    file = models.FileField(upload_to=letter_upload_to, null=True, blank=True)

    time_create = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"
        ordering = ["-time_create"]
        indexes = [
            models.Index(fields=["-time_create"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["letter_number"]),
            models.Index(fields=["internal_letter_number"]),
            models.Index(fields=["category"]),
        ]
        constraints = [
            # При желании можно запретить дубли в рамках категории:
            # models.UniqueConstraint(fields=["category", "letter_number"], name="uniq_letter_in_category"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:80] or "letter"
            tail = uuid.uuid4().hex[:8]
            self.slug = f"{base}-{tail}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
