from django.contrib import admin
from .models import Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'employee', 'activity_type', 'start_datetime', 'end_datetime', 'charge')
    list_filter = ('activity_type', 'employee')
    search_fields = ('title', 'description', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'start_datetime'