from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('details/<int:pk>/', views.projectDetails, name='projectDetails'),
    path('members/<int:pk>/', views.projectMembers, name='projectMembers'),
    path('calendar/<int:pk>/', views.projectCalendar, name='projectCalendar'),
]
