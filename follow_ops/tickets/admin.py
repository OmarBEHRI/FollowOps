from django.contrib import admin
from .models import Ticket, CommentTicket

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('assigned_to',)
    date_hierarchy = 'created_at'

class CommentTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

# Register models
admin.site.register(Ticket, TicketAdmin)
admin.site.register(CommentTicket, CommentTicketAdmin)
