from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Ressource, PasswordResetRequest

# Register the Ressource model with a custom admin class
class RessourceAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'status', 'appRole', 'availability_rate')
    list_filter = ('status', 'appRole', 'role')
    search_fields = ('email', 'first_name', 'last_name', 'role')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'location')}),
        ('Professional info', {'fields': ('role', 'skills', 'availability_rate', 'manager', 'status', 'entry_date')}),
        ('Permissions', {'fields': ('appRole', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'role', 'status', 'appRole'),
        }),
    )

admin.site.register(Ressource, RessourceAdmin)


class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_by_email', 'status', 'created_at', 'processed_by', 'processed_at')
    list_filter = ('status', 'created_at', 'processed_at', 'new_password_sent')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'requested_by_email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'processed_at')
    
    fieldsets = (
        ('Request Info', {
            'fields': ('user', 'requested_by_email', 'reason')
        }),
        ('Status', {
            'fields': ('status', 'new_password_sent')
        }),
        ('Admin Processing', {
            'fields': ('processed_by', 'admin_notes', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

admin.site.register(PasswordResetRequest, PasswordResetRequestAdmin)
