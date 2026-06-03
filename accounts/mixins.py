from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperAdmin, IsOrgAdmin, IsStaff, IsOrgOwner


class SuperAdminMixin:
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class OrgAdminMixin:
    permission_classes = [IsAuthenticated, IsOrgAdmin]


class StaffMixin:
    permission_classes = [IsAuthenticated, IsStaff]


class OrgOwnerMixin:
    permission_classes = [IsAuthenticated, IsOrgAdmin, IsOrgOwner]