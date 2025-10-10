from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from staffUsers.models import StaffProfile, StaffCuratorship
from organizations.models import Category, Organization


class Command(BaseCommand):
    help = "Создаёт примерных пользователей/кураторства"

    def ensure_profile(self, user, role):
        prof, _ = StaffProfile.objects.get_or_create(user=user)
        if prof.role != role:
            prof.role = role
            prof.save()
        return prof

    def handle(self, *args, **opts):
        User = get_user_model()

        admin, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.com"}
        )
        if not admin.has_usable_password():
            admin.set_password("admin123")
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()

        manager, _ = User.objects.get_or_create(
            username="manager", defaults={"email": "manager@example.com"}
        )
        if not manager.has_usable_password():
            manager.set_password("manager123")
            manager.is_staff = True
            manager.save()

        curator, _ = User.objects.get_or_create(
            username="curator", defaults={"email": "curator@example.com"}
        )
        if not curator.has_usable_password():
            curator.set_password("curator123")
            curator.save()

        admin_p = self.ensure_profile(admin,   StaffProfile.Role.ADMIN)
        manager_p = self.ensure_profile(manager, StaffProfile.Role.MANAGER)
        curator_p = self.ensure_profile(curator, StaffProfile.Role.CURATOR)

        bank_cat = Category.objects.order_by("id").first()
        org = Organization.objects.order_by("id").first()

        if org:
            StaffCuratorship.objects.get_or_create(
                staff=curator_p, organization=org, defaults={"can_edit": True}
            )
        if bank_cat:
            StaffCuratorship.objects.get_or_create(
                staff=curator_p, category=bank_cat, defaults={"can_edit": True}
            )

        self.stdout.write(self.style.SUCCESS("Seed done"))
