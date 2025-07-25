from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('create/', views.create_activity, name='create_activity'),
    path('get-options/<int:resource_id>/', views.get_projects_and_tickets, name='get_options'),
]