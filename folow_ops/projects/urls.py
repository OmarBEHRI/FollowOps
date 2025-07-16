from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('<pk>/', views.projectDetails, name='projectDetails'),
]
