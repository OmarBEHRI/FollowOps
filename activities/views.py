from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from .models import Activity
from ressources.models import Ressource
from projects.models import Project
from tickets.models import Ticket

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_activity(request):
     try:
         data = json.loads(request.body)
         # Utiliser l'utilisateur authentifié comme ressource
         resource = request.user
         # Empêcher la création pour une autre ressource via payload
         if 'resource_id' in data and str(data['resource_id']) != str(resource.id):
             return JsonResponse({
                 'success': False,
                 'message': "Vous ne pouvez créer des activités qu'en votre nom"
             }, status=403)
         
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
             # Vérifier que l'utilisateur est membre du projet (pas d'exception admin/manager)
             if not project.members.filter(id=request.user.id).exists():
                 return JsonResponse({
                     'success': False,
                     'message': 'Vous n\'êtes pas autorisé à créer une activité pour ce projet'
                 }, status=403)
             activity.project = project
         elif data['activity_type'] == 'TICKET' and data.get('ticket_id'):
             ticket = get_object_or_404(Ticket, id=data['ticket_id'])
             # Vérifier que l'utilisateur est assigné au ticket
             if not ticket.assigned_to.filter(id=request.user.id).exists():
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
 
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_ticket_activity(request, ticket_id):
     try:
         data = json.loads(request.body)
         
         # Récupérer le ticket
         ticket = get_object_or_404(Ticket, id=ticket_id)
         
         # Utiliser l'utilisateur connecté et vérifier l'assignation au ticket
         resource = request.user
         if not ticket.assigned_to.filter(id=resource.id).exists():
             return JsonResponse({
                 'success': False,
                 'message': 'Vous n\'êtes pas autorisé à créer une activité pour ce ticket'
             }, status=403)
         
         # Créer l'activité
         activity = Activity(
             title=data['title'],
             description=data.get('description', ''),
             employee=resource,
             activity_type='TICKET',
             start_datetime=datetime.fromisoformat(data['start_datetime']),
             end_datetime=datetime.fromisoformat(data['end_datetime']),
             ticket=ticket
         )
         
         activity.save()
         
         # Préparer les couleurs des membres assignés pour cohérence de l'UI
         ticket_members = list(ticket.assigned_to.all())
         member_colors = {}
         colors = [
             '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
             '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
             '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
         ]
         for i, member in enumerate(ticket_members):
             member_colors[member.id] = colors[i % len(colors)]
         
         # Déterminer le statut basé sur la date de début
         now = datetime.now().date()
         activity_date = activity.start_datetime.date()
         if activity_date < now:
             status = 'completed'
         elif activity_date == now:
             status = 'inprogress'
         else:
             status = 'planned'
         
         # Réponse avec les informations complètes de l'activité
         return JsonResponse({
             'success': True,
             'activity': {
                 'id': activity.id,
                 'title': activity.title,
                 'description': activity.description,
                 'start': activity.start_datetime.isoformat(),
                 'end': activity.end_datetime.isoformat(),
                 'status': status,
                 'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
                 'employee_id': activity.employee.id,
                 'employee_color': member_colors.get(activity.employee.id, '#A08D80')
             }
         })
         
     except Exception as e:
         return JsonResponse({
             'success': False,
             'message': str(e)
         }, status=400)

@require_http_methods(["GET"])
def get_ticket_activities(request, ticket_id):
    try:
        # Récupérer le ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Récupérer toutes les activités liées à ce ticket
        activities = Activity.objects.filter(ticket=ticket).order_by('start_datetime')
        
        # Get ticket assigned members for color assignment
        ticket_members = list(ticket.assigned_to.all())
        member_colors = {}
        
        # Define a set of distinct colors for members (same as project calendar)
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
            '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
        ]
        
        for i, member in enumerate(ticket_members):
            member_colors[member.id] = colors[i % len(colors)]
        
        activities_data = []
        for activity in activities:
            # Déterminer le statut basé sur les dates
            now = datetime.now().date()
            activity_date = activity.start_datetime.date()
            
            if activity_date < now:
                status = 'completed'
            elif activity_date == now:
                status = 'inprogress'
            else:
                status = 'planned'
            
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'start': activity.start_datetime.isoformat(),
                'end': activity.end_datetime.isoformat(),
                'status': status,
                'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
                'employee_id': activity.employee.id,
                'employee_color': member_colors.get(activity.employee.id, '#A08D80')  # Default color
            })
        
        return JsonResponse({
            'success': True,
            'activities': activities_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_http_methods(["GET"])
def get_project_activities(request, project_id):
    try:
        activities = Activity.objects.filter(
            project_id=project_id,
            activity_type='PROJECT'
        ).select_related('employee')
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'start_datetime': activity.start_datetime.isoformat(),
                'end_datetime': activity.end_datetime.isoformat(),
                'employee': activity.employee.get_full_name() if activity.employee else None,
                'status': 'completed' if hasattr(activity, 'is_completed') and activity.is_completed else 'inprogress'
            })
        
        return JsonResponse({
            'success': True,
            'activities': activities_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

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

@require_http_methods(["DELETE"])
@csrf_exempt
def delete_activity(request, activity_id):
    try:
        activity = get_object_or_404(Activity, id=activity_id)
        
        # Vérifier que l'utilisateur a le droit de supprimer cette activité
        # (par exemple, si c'est son activité ou s'il a les permissions)
        # Pour l'instant, on permet la suppression à tous
        
        activity.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Activité supprimée avec succès'
        })
        
    except Activity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Activité non trouvée'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Erreur lors de la suppression',
            'error': str(e)
        }, status=400)