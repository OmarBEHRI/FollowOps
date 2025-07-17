from django.urls import path
from . import views

urlpatterns = [
    path('', views.ressources, name='ressources'),
    path('details/<int:id>/', views.ressourcesDetails, name='ressourcesDetails'),
    path('delete/<int:id>/', views.ressourcesDelete, name='ressourcesDelete'),
]


