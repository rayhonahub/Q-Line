from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model  = Profile
    extra  = 0
    fields = ['avatar', 'bio', 'birth_date']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines     = [ProfileInline]
    list_display  = ['username', 'email', 'phone', 'role', 'is_active', 'created_at']
    list_filter   = ['role', 'is_active', 'language']
    search_fields = ['username', 'email', 'phone']
    ordering      = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Қ-Line маълумот', {
            'fields': ('role', 'phone', 'telegram_id', 'language')
        }),
    )

    # Role иваз кардан рӯйхатдан
    list_editable = ['role', 'is_active']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(id=request.user.id)