from django.db import models


class CertDocument(models.Model):
    """
    Письмо / документ CERT-CBU
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок"
    )
    number = models.CharField(
        max_length=100,
        verbose_name="Номер письма",
        blank=True
    )
    date = models.DateField(
        verbose_name="Дата письма",
        null=True,
        blank=True
    )
    from_organization = models.CharField(
        max_length=255,
        verbose_name="От кого",
        blank=True
    )
    to_organization = models.CharField(
        max_length=255,
        verbose_name="Кому",
        blank=True
    )
    description = models.TextField(
        verbose_name="Краткое описание",
        blank=True
    )

    file = models.FileField(
        upload_to="cert_documents/",
        verbose_name="Файл (PDF/документ)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено"
    )

    class Meta:
        verbose_name = "Документ CERT-CBU"
        verbose_name_plural = "Документы CERT-CBU"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.number or '---'} | {self.title}"
