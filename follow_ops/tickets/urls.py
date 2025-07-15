from django.urls import path
from . import views

urlpatterns = [
    path('', views.TicketListView.as_view(), name='ticket_list'),
    path('create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('<pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('<pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    path('<pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
]
