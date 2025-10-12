from django.db import models
from django.utils import timezone
from organizations.models import Organization

class OrgUnit(models.Model):
    class UnitType(models.TextChoices):
        DIRECTORATE = "directorate", "Дирекция"
        MANAGEMENT  = "management",  "Управление"
        DEPARTMENT  = "department",  "Отдел"
        SECTION     = "section",     "Сектор/Группа"
        OTHER       = "other",       "Иное"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="units"
    )
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=UnitType.choices, default=UnitType.OTHER)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    order = models.PositiveIntegerField(default=0)  # для сортировки сестринских узлов
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["organization", "parent__id", "order", "name"]

    def __str__(self):
        return f"{self.organization.name} :: {self.name}"


class OrgEmployee(models.Model):

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="employees"
    )
    unit = models.ForeignKey(
        OrgUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees"
    )
    full_name = models.CharField(max_length=200)
    position_title = models.CharField(max_length=200, blank=True, default="")  # Директор / Начальник управления / ...
    work_phone = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    lotus = models.CharField(max_length=255, blank=True, default="")            # если требуется
    is_head = models.BooleanField(default=False)                                 # флаг "руководитель узла"
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["organization", "unit__id", "is_head", "order", "full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.organization.name})"
