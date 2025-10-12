# staffUsers/models.py
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from organizations.models import Organization, Category


def unique_slug(model, base):
    base = slugify(base or "") or "item"
    slug = base
    i = 1
    while model.objects.filter(slug=slug).exists():
        i += 1
        slug = f"{base}-{i}"
    return slug


class ManagementUnit(models.Model):
    """Управление (например: Управление розничного бизнеса)."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(ManagementUnit, self.name)
        return super().save(*args, **kwargs)


class Department(models.Model):
    """Отдел внутри конкретного управления."""
    management = models.ForeignKey(
        ManagementUnit, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        ordering = ["management__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["management", "name"], name="uniq_department_per_management"
            )
        ]

    def __str__(self):
        return f"{self.management.name} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Department, f"{self.management.name}-{self.name}")
        return super().save(*args, **kwargs)


class StaffProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        MANAGER = "manager", "Менеджер"
        CURATOR = "curator", "Куратор"
        VIEWER = "viewer", "Читатель"

    class Position(models.TextChoices):
        DIRECTOR = "director", "Директор"
        DEPUTY_DIRECTOR = "deputy_director", "Заместитель директора (по управлению)"
        HEAD_OF_DEPT = "head_of_department", "Начальник отдела"
        CHIEF_EXPERT = "chief_expert", "Главный эксперт"
        LEAD_EXPERT = "lead_expert", "Ведущий эксперт"
        EXPERT_L1 = "expert_l1", "Эксперт первого уровня"
        EMPLOYEE = "employee", "Сотрудник"
        RECORDS_CLERK = "records_clerk", "Делопроизводитель"

    # базовая связка с User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff"
    )

    # ФИО
    first_name = models.CharField(max_length=100, blank=True, default="")
    second_name = models.CharField(max_length=100, blank=True, default="")  # отчество
    last_name = models.CharField(max_length=100, blank=True, default="")

    # контакты и идентификаторы
    lotus = models.CharField(max_length=255, blank=True, default="")
    work_email = models.EmailField(blank=True, default="")
    work_phone = models.CharField(max_length=32, blank=True, default="")

    # орг-позиции
    position = models.CharField(
        max_length=32, choices=Position.choices, default=Position.EMPLOYEE
    )
    management = models.ForeignKey(
        ManagementUnit, null=True, blank=True, on_delete=models.SET_NULL, related_name="staff"
    )
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="staff"
    )

    # роли доступа
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CURATOR)
    management_flag = models.BooleanField(default=False)  # если нужно оставить ваш прежний флаг

    # кеш-счётчики кураторств
    curated_orgs_count = models.PositiveIntegerField(default=0)
    curated_cats_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["last_name", "first_name", "second_name"]

    def __str__(self):
        return self.fio or self.user.get_username()

    @property
    def fio(self):
        parts = [self.last_name, self.first_name, self.second_name]
        return " ".join([p for p in parts if p]) or (self.user.get_full_name() or self.user.get_username())

    # Правила валидности орг-иерархии
    def clean(self):
        # Делопроизводитель и Директор: вне управлений/отделов
        if self.position in {self.Position.DIRECTOR, self.Position.RECORDS_CLERK}:
            if self.management_id or self.department_id:
                raise ValidationError("Директор/Делопроизводитель не должны быть привязаны к управлению/отделу.")

        # Замдиректора – привязан к управлению, но не к отделу
        if self.position == self.Position.DEPUTY_DIRECTOR:
            if not self.management_id or self.department_id:
                raise ValidationError("Замдиректор должен быть привязан к управлению и не иметь отдела.")

        # Начальник отдела – привязан к управлению и отделу (отдел внутри управления)
        if self.position == self.Position.HEAD_OF_DEPT:
            if not self.management_id or not self.department_id:
                raise ValidationError("Начальник отдела должен быть привязан к управлению и отделу.")
            if self.department and self.department.management_id != self.management_id:
                raise ValidationError("Отдел должен принадлежать выбранному управлению.")

        # Эксперты/Сотрудники – должны быть в отделе (и управлении, соответствующем отделу)
        if self.position in {
            self.Position.CHIEF_EXPERT, self.Position.LEAD_EXPERT,
            self.Position.EXPERT_L1, self.Position.EMPLOYEE
        }:
            if not self.department_id or not self.management_id:
                raise ValidationError("Сотрудник/Эксперт должен быть привязан к управлению и отделу.")
            if self.department and self.department.management_id != self.management_id:
                raise ValidationError("Отдел должен принадлежать выбранному управлению.")

    # Права (сверху вниз)
    def is_admin_like(self):
        return self.role in (self.Role.ADMIN, self.Role.MANAGER) or self.position == self.Position.DIRECTOR

    def can_edit_org(self, org: Organization):
        if self.is_admin_like():
            return True
        # замдиректор может редактировать всё в своём управлении (по договорённости),
        # если организация помечена его управлением через кураторство категории/организации
        if self.position == self.Position.DEPUTY_DIRECTOR:
            return self.curator_links.filter(can_edit=True).exists()
        # начальник отдела — если есть кураторство на категорию или орг
        if self.position == self.Position.HEAD_OF_DEPT:
            return (
                self.curator_links.filter(organization=org, can_edit=True).exists() or
                self.curator_links.filter(category=org.category, can_edit=True).exists()
            )
        # прочие — только явные кураторские связи
        return (
            self.curator_links.filter(organization=org, can_edit=True).exists() or
            self.curator_links.filter(category=org.category, can_edit=True).exists()
        )

    def can_edit_category(self, cat: Category):
        if self.is_admin_like():
            return True
        if self.position == self.Position.DEPUTY_DIRECTOR:
            return self.curator_links.filter(category=cat, can_edit=True).exists()
        if self.position == self.Position.HEAD_OF_DEPT:
            return self.curator_links.filter(category=cat, can_edit=True).exists()
        return self.curator_links.filter(category=cat, can_edit=True).exists()


class StaffCuratorship(models.Model):
    """
    Связь «сотрудник — организация ИЛИ категория».
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
            raise ValidationError("Укажите ИЛИ organization, ИЛИ category (но не оба).")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # обновим счётчики
        StaffProfile.objects.filter(pk=self.staff_id).update(
            curated_orgs_count=StaffCuratorship.objects.filter(
                staff_id=self.staff_id, organization__isnull=False).count(),
            curated_cats_count=StaffCuratorship.objects.filter(
                staff_id=self.staff_id, category__isnull=False).count(),
        )


class AuditEntry(models.Model):
    """Простой аудит."""
    class Target(models.TextChoices):
        ORG = "org", "Организация"
        CAT = "cat", "Категория"

    actor = models.ForeignKey("StaffProfile", on_delete=models.SET_NULL, null=True, blank=True)
    target = models.CharField(max_length=3, choices=Target.choices)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32)  # created/updated/deleted
    fields = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created"]
