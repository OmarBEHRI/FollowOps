from django.contrib import admin
from .models import Activity, UserActivityLog

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'employee', 'activity_type', 'start_datetime', 'end_datetime', 'charge')
    list_filter = ('activity_type', 'employee')
    search_fields = ('title', 'description', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'start_datetime'

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_hour', 'end_hour', 'duration_hours', 'allocation_status', 'log_type')
    list_filter = ('allocation_status', 'log_type', 'date', 'employee')
    search_fields = ('employee__first_name', 'employee__last_name', 'activity_title')
    date_hierarchy = 'date'
    readonly_fields = ('efficiency_ratio', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'activity', 'date', 'activity_title')
        }),
        ('Time Tracking', {
            'fields': ('start_hour', 'end_hour', 'duration_hours')
        }),
        ('Status', {
            'fields': ('log_type', 'allocation_status')
        }),
        ('Metadata', {
            'fields': ('project_id', 'ticket_id')
        }),
        ('Efficiency Tracking', {
            'fields': ('planned_hours', 'actual_hours', 'efficiency_ratio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )