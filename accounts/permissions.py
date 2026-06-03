from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """Фақат Super Admin"""
    message = "Фақат Super Admin иҷозат дорад!"

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'super_admin'
        )


class IsOrgAdmin(BasePermission):
    """Super Admin ё Org Admin"""
    message = "Фақат Ташкилот Админ иҷозат дорад!"

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['super_admin', 'org_admin']
        )


class IsStaff(BasePermission):
    """Super Admin, Org Admin ё Staff"""
    message = "Фақат Ходимон иҷозат дорад!"

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['super_admin', 'org_admin', 'staff']
        )


class IsCustomer(BasePermission):
    """Фақат Customer"""
    message = "Фақат Муштарӣ иҷозат дорад!"

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'customer'
        )


class IsOwnerOrReadOnly(BasePermission):
    """Соҳиби объект таҳрир мекунад, дигарон фақат мехонанд"""
    message = "Шумо соҳиби ин объект нестед!"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user


class IsOrgOwner(BasePermission):
    """Фақат соҳиби ташкилот"""
    message = "Шумо соҳиби ин ташкилот нестед!"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'super_admin':
            return True
        # Organization
        if hasattr(obj, 'owner'):
            return obj.owner == user
        # Branch
        if hasattr(obj, 'organization'):
            return obj.organization.owner == user
        # Window
        if hasattr(obj, 'branch'):
            return obj.branch.organization.owner == user
        return False


class IsTicketOwner(BasePermission):
    """Фақат соҳиби ticket"""
    message = "Ин навбат ба шумо тааллуқ надорад!"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ['super_admin', 'org_admin', 'staff']:
            return True
        return obj.customer == user