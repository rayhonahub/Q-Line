from django.contrib import admin
from .models import Queue, Ticket, Appointment


class TicketInline(admin.TabularInline):
    model        = Ticket
    extra        = 0
    fields       = ['number', 'status', 'customer', 'window', 'created_at']
    readonly_fields = ['number', 'created_at']
    can_delete   = False


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    inlines       = [TicketInline]
    list_display  = ['name', 'branch', 'prefix', 'waiting_count', 'is_active']
    list_filter   = ['is_active', 'branch__organization']
    search_fields = ['name', 'branch__name']
    list_editable = ['is_active']

    def waiting_count(self, obj):
        return obj.tickets.filter(status='waiting').count()
    waiting_count.short_description = '⏳ Интизор'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(branch__organization__owner=request.user)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display    = ['number', 'queue', 'customer', 'window', 'status', 'rating', 'created_at']
    list_filter     = ['status', 'rating', 'queue__branch__organization']
    search_fields   = ['number', 'customer__username']
    readonly_fields = ['number', 'created_at', 'called_at', 'completed_at']
    ordering        = ['-created_at']

    # Status рӯйхатдан иваз кардан
    list_editable = ['status']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(queue__branch__organization__owner=request.user)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['customer', 'queue', 'scheduled_at', 'status', 'created_at']
    list_filter   = ['status', 'queue__branch__organization']
    search_fields = ['customer__username']
    list_editable = ['status']
    ordering      = ['-scheduled_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'super_admin':
            return qs
        return qs.filter(queue__branch__organization__owner=request.user)