from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('create/', views.create_project, name='create_project'),
    path('details/<int:pk>/', views.projectDetails, name='projectDetails'),
    path('members/<int:pk>/', views.projectMembers, name='projectMembers'),
    path('calendar/<int:pk>/', views.projectCalendar, name='projectCalendar'),
    path('comments/<int:pk>/', views.projectComments, name='projectComments'),
    path('edit/<int:pk>/', views.edit_project, name='edit_project'),
    path('delete/<int:pk>/', views.delete_project, name='delete_project'),  # Nouvelle route
    # Tag API endpoints
    path('api/tags/search/', views.search_tags, name='search_tags'),
    path('api/tags/all/', views.get_all_tags, name='get_all_tags'),
    path('api/tags/create/', views.create_tag, name='create_tag'),
    # Global search API endpoint
    path('api/global-search/', views.global_search, name='global_search'),
    # Nouvel endpoint pour les projets de l'utilisateur
    path('api/projects/', views.get_user_projects_api, name='get_user_projects_api'),
    path('<int:pk>/calendar/activities/', views.get_project_activities, name='get_project_activities'),
]
