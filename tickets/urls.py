from django.urls import path
from . import views

urlpatterns = [
    path('', views.tickets, name='tickets'),
    path('details/<int:ticket_id>/', views.ticketDetails, name='ticketDetails'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('edit/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
    path('delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('add_comment/<int:ticket_id>/', views.add_comment_ajax, name='add_comment_ajax'),
]