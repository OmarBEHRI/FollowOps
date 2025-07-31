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
    # API endpoint for resource activities
    path('api/<int:resource_id>/activities/', views.get_resource_activities, name='get_resource_activities'),
]


