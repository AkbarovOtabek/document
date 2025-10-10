from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from organizations.models import Organization, Category
from .models import StaffProfile, AuditEntry


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_staff_profile(sender, instance, created, **kwargs):
    if created:
        StaffProfile.objects.create(user=instance)


# примеры аудита — по желанию, можно вызывать вручную из ViewSet'ов
@receiver(post_save, sender=Organization)
def audit_org_save(sender, instance, created, **kwargs):
    # здесь нельзя получить actor, поэтому в реальных апдейтах лучше писать из view.
    pass


@receiver(post_delete, sender=Organization)
def audit_org_delete(sender, instance, **kwargs):
    pass
