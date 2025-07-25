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
    # Tag API endpoints
    path('api/tags/search/', views.search_tags, name='search_tags'),
    path('api/tags/create/', views.create_tag, name='create_tag'),
]
