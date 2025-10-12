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
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(get_staff(request.user))

class CanEditCategory(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        staff = get_staff(request.user)
        return bool(staff and staff.can_edit_category(obj))

class CanEditOrganization(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        staff = get_staff(request.user)
        return bool(staff and staff.can_edit_org(obj))

class CanEditOrgObject(BasePermission):
    """Проверяем право редактировать организацию для OrgUnit/OrgEmployee."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        staff = get_staff(request.user)
        if not staff:
            return False
        org = getattr(obj, "organization", None)
        if org is None:
            unit = getattr(obj, "unit", None)
            if unit is not None:
                org = getattr(unit, "organization", None)
        return bool(org and staff.can_edit_org(org))
