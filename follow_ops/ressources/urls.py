from django.urls import path
from . import views

urlpatterns = [
    path('', views.ressources, name='ressources'),
    path('details/', views.ressourcesDetails, name='ressourcesDetails'),
    path('add/', views.add_resource, name='add_resource'),
]


