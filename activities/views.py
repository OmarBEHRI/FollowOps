from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime
from .models import Activity
from ressources.models import Ressource
from projects.models import Project
from tickets.models import Ticket

@require_http_methods(["POST"])
@csrf_exempt
def create_activity(request):
    try:
        data = json.loads(request.body)
        
        # Récupérer la ressource
        resource = get_object_or_404(Ressource, id=data['resource_id'])
        
        # Créer l'activité
        activity = Activity(
            title=data['title'],
            description=data.get('description', ''),
            employee=resource,
            activity_type=data['activity_type'],
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime'])
        )
        
        # Associer le projet ou ticket selon le type
        if data['activity_type'] == 'PROJECT' and data.get('project_id'):
            activity.project = get_object_or_404(Project, id=data['project_id'])
        elif data['activity_type'] == 'TICKET' and data.get('ticket_id'):
            activity.ticket = get_object_or_404(Ticket, id=data['ticket_id'])
        
        activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Activité créée avec succès',
            'activity_id': activity.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def get_projects_and_tickets(request, resource_id):
    """Récupérer les projets et tickets disponibles pour une ressource"""
    try:
        resource = get_object_or_404(Ressource, id=resource_id)
        
        # Récupérer tous les projets (ou filtrer selon vos besoins)
        projects = Project.objects.all().values('id', 'title')
        tickets = Ticket.objects.all().values('id', 'title')
        
        return JsonResponse({
            'projects': list(projects),
            'tickets': list(tickets)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)