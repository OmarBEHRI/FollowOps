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
        
        # Associer le projet ou ticket selon le type avec validation des permissions
        if data['activity_type'] == 'PROJECT' and data.get('project_id'):
            project = get_object_or_404(Project, id=data['project_id'])
            # Vérifier que l'utilisateur est membre du projet
            if not project.members.filter(id=resource.id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Vous n\'êtes pas autorisé à créer une activité pour ce projet'
                }, status=403)
            activity.project = project
        elif data['activity_type'] == 'TICKET' and data.get('ticket_id'):
            ticket = get_object_or_404(Ticket, id=data['ticket_id'])
            # Vérifier que l'utilisateur est assigné au ticket
            if not ticket.assigned_to.filter(id=resource.id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Vous n\'êtes pas autorisé à créer une activité pour ce ticket'
                }, status=403)
            activity.ticket = ticket
        
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
    try:
        resource = get_object_or_404(Ressource, id=resource_id)
        
        # Filtrer les projets où l'utilisateur est membre
        user_projects = Project.objects.filter(members=resource)
        projects = [{'id': p.id, 'name': p.title} for p in user_projects]
        
        # Filtrer les tickets où l'utilisateur est assigné
        user_tickets = Ticket.objects.filter(assigned_to=resource)
        tickets = [{'id': t.id, 'title': t.title} for t in user_tickets]
        
        return JsonResponse({
            'success': True,
            'projects': projects,
            'tickets': tickets
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)