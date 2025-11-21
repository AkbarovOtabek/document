# cert_documents/models.py
from django.conf import settings
from django.db import models

from organizations.models import Organization


class CertLetter(models.Model):
    SYSTEM_CHOICES = (
        ("CERT-CBU", "CERT-CBU"),
    )

    system = models.CharField(
        max_length=50,
        choices=SYSTEM_CHOICES,
        default="CERT-CBU",
    )
    number = models.CharField(max_length=100, verbose_name="Номер письма")
    date = models.DateField(verbose_name="Дата выхода письма")
    subject = models.CharField(max_length=500, verbose_name="Тема / титул")

    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="cert_performer_letters",
        verbose_name="Исполнитель"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание / требуемые действия"
    )

    has_deadline = models.BooleanField(
        default=False,
        verbose_name="Есть срок письма"
    )
    deadline = models.DateField(
        null=True, blank=True,
        verbose_name="Дата срока"
    )

 # 🔹 НОВОЕ ПОЛЕ: нужно ли требовать ответные письма
    need_replies = models.BooleanField(
        default=True,
        verbose_name="Требуются ответные письма от организаций",
        help_text="Если выключено, ответы не отслеживаются и статусы по организациям не считаются.",
    )

    # Куда отправлено — только организации
    dest_organizations = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="cert_letters",
        verbose_name="Организации"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="cert_letters_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="cert_letters_updated"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-date", "-id")
        verbose_name = "Письмо CERT-CBU"
        verbose_name_plural = "Письма CERT-CBU"

    def __str__(self):
        return f"{self.system} {self.number} от {self.date}"


class CertLetterFile(models.Model):
    letter = models.ForeignKey(
        CertLetter,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(
        upload_to="cert_letters/",
        verbose_name="Файл"
    )
    original_name = models.CharField(
        max_length=255,
        blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Файл письма CERT-CBU"
        verbose_name_plural = "Файлы писем CERT-CBU"

    def __str__(self):
        return self.original_name or self.file.name


class CertLetterReply(models.Model):
    """
    Ответное письмо на письмо CERT-CBU
    (например, ответ от конкретного банка / организации).
    """
    letter = models.ForeignKey(
        CertLetter,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="Исходное письмо CERT-CBU",
    )

    # От какой организации пришёл ответ
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="cert_letter_replies",
        verbose_name="Организация (ответчик)",
    )

    # 🔹 Наши новые поля
    reply_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Номер ответного письма",
    )
    internal_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Внутренний номер (если есть)",
    )

    # Файл ответа
    file = models.FileField(
        upload_to="cert_letters/replies/",
        verbose_name="Файл ответного письма",
    )

    # Дата, когда ответ официально получен (по документу)
    received_date = models.DateField(
        verbose_name="Дата приёма ответа",
    )

    # Кто и когда занёс в систему
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="cert_letter_replies_added",
        verbose_name="Пользователь, добавивший ответ",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления в систему",
    )

    class Meta:
        verbose_name = "Ответное письмо CERT-CBU"
        verbose_name_plural = "Ответные письма CERT-CBU"
        ordering = ("-received_date", "-id")

    def __str__(self):
        org_name = getattr(self.organization, "name", "—")
        return f"Ответ на {self.letter.number} от {org_name}"
