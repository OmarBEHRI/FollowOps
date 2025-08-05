from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('create/', views.create_activity, name='create_activity'),
    path('ticket/<int:ticket_id>/create/', views.create_ticket_activity, name='create_ticket_activity'),
    path('ticket/<int:ticket_id>/activities/', views.get_ticket_activities, name='get_ticket_activities'),
    path('delete/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('get-options/<int:resource_id>/', views.get_projects_and_tickets, name='get_options'),
]