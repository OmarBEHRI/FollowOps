from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('ressources/', views.ressources, name='ressources'),
    path('ressources/<int:pk>/', views.ressource_detail, name='ressource_detail'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('tickets/', views.tickets, name='tickets'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
]
