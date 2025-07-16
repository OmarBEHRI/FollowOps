from django.urls import path
from . import views

urlpatterns = [
    path('', views.ressources, name='ressources'),
    path('<pk>/', views.ressourcesDetails, name='ressourcesDetails'),
]


