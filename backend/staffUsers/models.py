from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from organizations.models import Organization, Category


class StaffProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin",   "Администратор"
        MANAGER = "manager", "Менеджер"
        CURATOR = "curator", "Куратор"
        VIEWER = "viewer",  "Читатель"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff")
    first_name = models.CharField(max_length=100, blank=True, default="")
    second_name = models.CharField(
        max_length=100, blank=True, default="")   # отчество
    last_name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="")
    management = models.BooleanField(default=False)  # флаг «руководство»
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CURATOR)

    # агрегированная инфа для быстрых проверок (кешируем кол-во связей)
    curated_orgs_count = models.PositiveIntegerField(default=0)
    curated_cats_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.fio or self.user.get_username()

    @property
    def fio(self):
        parts = [self.last_name, self.first_name, self.second_name]
        clean = [p for p in parts if p]
        full = " ".join(clean)
        return full if full else (self.user.get_full_name() or self.user.get_username())

    # удобные методы прав
    def is_admin_like(self):     # всё можно
        return self.role in (self.Role.ADMIN, self.Role.MANAGER)

    def can_edit_org(self, org: Organization):
        if self.is_admin_like():
            return True
        return (
            self.curator_links.filter(organization=org, can_edit=True).exists() or
            self.curator_links.filter(
                category=org.category, can_edit=True).exists()
        )

    def can_edit_category(self, cat: Category):
        if self.is_admin_like():
            return True
        return self.curator_links.filter(category=cat, can_edit=True).exists()


class StaffCuratorship(models.Model):
    """
    Связь «сотрудник — организация/категория».
    organization XOR category; can_edit — можно ли редактировать/удалять.
    """
    staff = models.ForeignKey(
        StaffProfile, on_delete=models.CASCADE, related_name="curator_links")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True, related_name="curator_links")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True, related_name="curator_links")
    can_edit = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["staff", "organization"], name="uniq_staff_org",
                condition=models.Q(organization__isnull=False)
            ),
            models.UniqueConstraint(
                fields=["staff", "category"], name="uniq_staff_cat",
                condition=models.Q(category__isnull=False)
            ),
        ]

    def clean(self):
        if bool(self.organization) == bool(self.category):
            raise ValidationError(
                "Укажите ИЛИ organization, ИЛИ category (но не оба).")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # обновим денормализованные счётчики
        StaffProfile.objects.filter(pk=self.staff_id).update(
            curated_orgs_count=StaffCuratorship.objects.filter(
                staff_id=self.staff_id, organization__isnull=False).count(),
            curated_cats_count=StaffCuratorship.objects.filter(
                staff_id=self.staff_id, category__isnull=False).count(),
        )


class AuditEntry(models.Model):
    """
    Простая таблица аудита действий по организациям/категориям.
    """
    class Target(models.TextChoices):
        ORG = "org", "Организация"
        CAT = "cat", "Категория"

    actor = models.ForeignKey(
        StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)
    target = models.CharField(max_length=3, choices=Target.choices)
    org = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32)  # created/updated/deleted и т.п.
    fields = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created"]
