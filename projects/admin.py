from django.contrib import admin
from .models import Project, Tag, CommentProject

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'priority', 'project_manager', 'progress', 'expected_start_date', 'expected_end_date')
    list_filter = ('status', 'priority', 'type')
    search_fields = ('title', 'description')
    filter_horizontal = ('members', 'tags')
    date_hierarchy = 'expected_start_date'

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

class CommentProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

# Register models
admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(CommentProject, CommentProjectAdmin)
