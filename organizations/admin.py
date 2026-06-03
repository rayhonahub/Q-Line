from django.contrib import admin
from .models import Organization, Branch, Window


class BranchInline(admin.TabularInline):
    model  = Branch
    extra  = 0
    fields = ['name', 'address', 'phone', 'is_active']


class WindowInline(admin.TabularInline):
    model  = Window
    extra  = 0
    fields = ['name', 'staff', 'is_active']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines       = [BranchInline]
    list_display  = ['name', 'slug', 'owner', 'plan', 'is_active', 'created_at']
    list_filter   = ['plan', 'is_active']
    search_fields = ['name', 'slug', 'owner__username']
    list_editable = ['plan', 'is_active']
    ordering      = ['-created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(owner=request.user)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    inlines       = [WindowInline]
    list_display  = ['name', 'organization', 'phone', 'is_active']
    list_filter   = ['is_active', 'organization']
    search_fields = ['name', 'organization__name']
    list_editable = ['is_active']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(organization__owner=request.user)


@admin.register(Window)
class WindowAdmin(admin.ModelAdmin):
    list_display  = ['name', 'branch', 'staff', 'is_active']
    list_filter   = ['is_active', 'branch__organization']
    search_fields = ['name', 'branch__name']
    list_editable = ['is_active']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(branch__organization__owner=request.user)
