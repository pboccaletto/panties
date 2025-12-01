"""
Admin configuration for Panties core models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectMember, ErrorEvent


class ProjectMemberInline(admin.TabularInline):
    """Inline admin for project members."""
    model = ProjectMember
    extra = 1
    fields = ('user', 'role', 'invited_by', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model."""
    list_display = ('name', 'owner', 'api_key_display', 'error_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__email')
    readonly_fields = ('api_key', 'created_at', 'updated_at')
    inlines = [ProjectMemberInline]

    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'description', 'owner')
        }),
        ('API Configuration', {
            'fields': ('api_key',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def api_key_display(self, obj):
        """Display truncated API key for security."""
        return f"{obj.api_key[:8]}...{obj.api_key[-8:]}"
    api_key_display.short_description = 'API Key'

    def error_count(self, obj):
        """Display count of errors for this project."""
        count = obj.errors.count()
        return format_html('<b>{}</b>', count)
    error_count.short_description = 'Errors'


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin interface for ProjectMember model."""
    list_display = ('user', 'project', 'role', 'invited_by', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'project__name', 'invited_by__email')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Membership Information', {
            'fields': ('project', 'user', 'role')
        }),
        ('Invitation Details', {
            'fields': ('invited_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ErrorEvent)
class ErrorEventAdmin(admin.ModelAdmin):
    """Admin interface for ErrorEvent model."""
    list_display = ('event_id_short', 'project', 'event_type', 'exception_type', 'timestamp', 'has_stacktrace')
    list_filter = ('event_type', 'timestamp', 'project')
    search_fields = ('event_id', 'exception_type', 'message', 'project__name')
    readonly_fields = ('event_id', 'timestamp')
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'project', 'event_type', 'timestamp')
        }),
        ('Error Details', {
            'fields': ('exception_type', 'message', 'level')
        }),
        ('Stack Trace', {
            'fields': ('stacktrace',),
            'classes': ('collapse',)
        }),
        ('Context Data', {
            'fields': ('tags', 'extra', 'environment', 'service_name'),
            'classes': ('collapse',)
        }),
    )

    def event_id_short(self, obj):
        """Display shortened event ID."""
        return f"{obj.event_id[:8]}..."
    event_id_short.short_description = 'Event ID'

    def has_stacktrace(self, obj):
        """Display whether this event has a stacktrace."""
        if obj.stacktrace:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_stacktrace.short_description = 'Stack Trace'
    has_stacktrace.admin_order_field = 'stacktrace'
