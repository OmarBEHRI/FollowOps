from django.urls import path
from . import views

urlpatterns = [
    path('', views.ressources, name='ressources'),
    path('details/', views.ressourcesDetails, name='ressourcesDetails'),
    path('details/<int:resource_id>/', views.ressourcesDetails, name='ressourcesDetails_with_id'),
    path('add/', views.add_resource, name='add_resource'),
    path('edit/<int:resource_id>/', views.edit_resource, name='edit_resource'),
    path('delete/<int:resource_id>/', views.delete_resource, name='delete_resource'),
    path('export/', views.export_ressources_excel, name='export_ressources'),
    # API endpoints for resource activities and availability
    path('api/<int:resource_id>/activities/', views.get_resource_activities, name='get_resource_activities'),
    path('api/<int:resource_id>/availability/', views.get_resource_availability, name='get_resource_availability'),
    path('api/<int:resource_id>/hourly-breakdown/', views.get_resource_hourly_breakdown, name='get_resource_hourly_breakdown'),
    path('api/<int:resource_id>/activity-trends/', views.get_resource_activity_trends, name='get_resource_activity_trends'),
    path('api/<int:resource_id>/export-report/', views.export_resource_activity_report, name='export_resource_activity_report'),
]


