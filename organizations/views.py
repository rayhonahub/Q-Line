from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Organization, Branch, Window
from .serializers import (
    OrganizationSerializer, OrganizationListSerializer,
    BranchSerializer, WindowSerializer
)
from accounts.permissions import IsOrgAdmin, IsOrgOwner, IsStaff
from drf_spectacular.utils import extend_schema, OpenApiResponse
from accounts.permissions import IsOrgAdmin, IsOrgOwner, IsStaff, IsSuperAdmin
from accounts.mixins import OrgAdminMixin, OrgOwnerMixin, StaffMixin


@extend_schema(tags=['Organizations'], summary='Ташкилотҳои ман')

class OrganizationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsOrgAdmin] 

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrganizationListSerializer
        return OrganizationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Organization.objects.all()         # ← Ҳамаро мебинад
        return Organization.objects.filter(owner=user) # ← Фақат худашро



@extend_schema(tags=['Organizations'], summary='Ташкилот — кор, таҳрир, ҳазф')
class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin, IsOrgOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Organization.objects.all()
        return Organization.objects.filter(owner=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Ташкилот ғайрифаъол шуд!"})


# ─────────────────────────────────────────
# BRANCH
# ─────────────────────────────────────────
@extend_schema(tags=['Branches'], summary='Шӯъбаҳои ташкилот')
class BranchListCreateView(generics.ListCreateAPIView):
    serializer_class   = BranchSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin, IsOrgOwner]

    def get_queryset(self):
        org = get_object_or_404(Organization, pk=self.kwargs['org_id'])
        self.check_object_permissions(self.request, org)
        return Branch.objects.filter(organization=org)

    def perform_create(self, serializer):
        org = get_object_or_404(Organization, pk=self.kwargs['org_id'])
        self.check_object_permissions(self.request, org)
        serializer.save(organization=org)


@extend_schema(tags=['Branches'], summary='Шӯъба — кор, таҳрир, ҳазф')
class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = BranchSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin, IsOrgOwner]

    def get_queryset(self):
        return Branch.objects.filter(organization__id=self.kwargs['org_id'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Шӯъба ғайрифаъол шуд!"})


# ─────────────────────────────────────────
# WINDOW
# ─────────────────────────────────────────

@extend_schema(tags=['Windows'], summary='Дарвозаҳои шӯъба')
class WindowListCreateView(generics.ListCreateAPIView):
    serializer_class   = WindowSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin, IsOrgOwner]

    def get_queryset(self):
        return Window.objects.filter(branch__id=self.kwargs['branch_id'])

    def perform_create(self, serializer):
        branch = get_object_or_404(Branch, pk=self.kwargs['branch_id'])
        serializer.save(branch=branch)


@extend_schema(tags=['Windows'], summary='Дарвоза — кор, таҳрир, ҳазф')
class WindowDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = WindowSerializer
    permission_classes = [IsAuthenticated, IsOrgAdmin, IsOrgOwner]

    def get_queryset(self):
        return Window.objects.filter(branch__id=self.kwargs['branch_id'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Дарвоза ғайрифаъол шуд!"})


from rest_framework.permissions import AllowAny


class PublicOrgsView(generics.ListAPIView):
    """Бот — токен лозим нест"""
    serializer_class   = OrganizationListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Organization.objects.filter(is_active=True)


class PublicBranchesView(generics.ListAPIView):
    """Бот  — токен лозим нест"""
    serializer_class   = BranchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Branch.objects.filter(
            organization__id=self.kwargs['pk'],
            is_active=True
        )        