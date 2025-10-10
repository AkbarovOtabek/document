from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import StaffProfile


def get_staff(user):
    if not (user and user.is_authenticated):
        return None
    try:
        return user.staff
    except StaffProfile.DoesNotExist:
        return None


class IsStaffOrReadOnly(BasePermission):
    """Чтение — всем; изменения — только аутентифицированным staff."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(get_staff(request.user))


class CanEditCategory(BasePermission):
    """Объектное право для Category."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        staff = get_staff(request.user)
        return bool(staff and staff.can_edit_category(obj))


class CanEditOrganization(BasePermission):
    """Объектное право для Organization."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        staff = get_staff(request.user)
        return bool(staff and staff.can_edit_org(obj))
