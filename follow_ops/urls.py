from django.contrib import admin
from django.urls import path, include

urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('activities/', include('activities.urls')),
    path('ressources/', include('ressources.urls')),
    path('projects/', include('projects.urls')),
    path('tickets/', include('tickets.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('homepage.urls')),
]
