from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from projects.models import Project, CommentProject
from ressources.models import Ressource
from tickets.models import Ticket, CommentTicket
from activities.models import Activity
from django.db.models import Q
import json

@login_required
def dashboard(request):
    # Get the current user
    user = request.user
    
    # Determine which dashboard template to render based on user's role
    if user.appRole == 'ADMIN':
        # Calculate dynamic data for admin dashboard
        context = get_admin_dashboard_data()
        return render(request, 'dashboard.html', context)  # Admin dashboard (original)
    elif user.appRole == 'MANAGER':
        # Calculate dynamic data for manager dashboard
        context = get_manager_dashboard_data(user)
        return render(request, 'dashboard_manager.html', context)  # Manager dashboard
    else:  # USER role
        # Calculate dynamic data for user dashboard
        context = get_user_dashboard_data(user)
        return render(request, 'dashboard_user.html', context)  # User dashboard

def get_admin_dashboard_data():
    """Calculate and return data for admin dashboard"""
    
    # 1. Projets en cours: Projects with status "En cours"
    projets_en_cours = Project.objects.filter(status='En cours').count()
    
    # 2. Taux d'occupation des ressources: Average of all resources availability_rate
    avg_availability = Ressource.objects.filter(availability_rate__isnull=False).aggregate(
        avg_rate=Avg('availability_rate')
    )['avg_rate'] or 0
    taux_occupation = round(avg_availability, 1)
    
    # 3. Taux d'avancement des projets: Average progress of "En cours" projects
    avg_progress = Project.objects.filter(status='En cours').aggregate(
        avg_progress=Avg('progress')
    )['avg_progress'] or 0
    taux_avancement = round(avg_progress, 1)
    
    # 4. Budget Restant: Leave hardcoded as requested
    budget_restant = "50 000 DH"
    
    # 5. Répartition des tickets par statut: Percentage of ticket statuses
    total_tickets = Ticket.objects.count()
    ticket_stats = {}
    if total_tickets > 0:
        ticket_counts = Ticket.objects.values('status').annotate(count=Count('status'))
        for item in ticket_counts:
            percentage = round((item['count'] / total_tickets) * 100, 1)
            ticket_stats[item['status']] = {
                'count': item['count'],
                'percentage': percentage
            }
    
    # Convert ticket stats to JSON for JavaScript
    ticket_stats_json = json.dumps(ticket_stats)
    
    # 6. Allocation des ressources par rôle: Count resources per role
    role_allocation = Ressource.objects.values('role').annotate(count=Count('role')).order_by('-count')
    total_resources = Ressource.objects.count()
    
    # 7. Activités Récentes: Latest comments and activities
    recent_activities = []
    
    # Get recent project comments
    recent_project_comments = CommentProject.objects.select_related('author', 'project').order_by('-created_at')[:5]
    for comment in recent_project_comments:
        recent_activities.append({
            'type': 'project_comment',
            'text': f"Nouveau commentaire sur le projet '{comment.project.title}' par {comment.author.first_name} {comment.author.last_name}",
            'author': comment.author,
            'created_at': comment.created_at,
            'related_object': comment.project
        })
    
    # Get recent ticket comments
    recent_ticket_comments = CommentTicket.objects.select_related('author', 'ticket').order_by('-created_at')[:5]
    for comment in recent_ticket_comments:
        recent_activities.append({
            'type': 'ticket_comment',
            'text': f"Nouveau commentaire sur le ticket '{comment.ticket.title}' par {comment.author.first_name} {comment.author.last_name}",
            'author': comment.author,
            'created_at': comment.created_at,
            'related_object': comment.ticket
        })
    
    # Get recent activities
    recent_activity_logs = Activity.objects.select_related('employee', 'project', 'ticket').order_by('-created_at')[:5]
    for activity in recent_activity_logs:
        if activity.project:
            text = f"Activité '{activity.title}' créée sur le projet '{activity.project.title}' par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = activity.project
        elif activity.ticket:
            text = f"Activité '{activity.title}' créée sur le ticket '{activity.ticket.title}' par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = activity.ticket
        else:
            text = f"Activité '{activity.title}' créée par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = None
            
        recent_activities.append({
            'type': 'activity',
            'text': text,
            'author': activity.employee,
            'created_at': activity.created_at,
            'related_object': related_obj
        })
    
    # Sort all activities by creation date and take the most recent 8
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:8]
    
    return {
        'projets_en_cours': projets_en_cours,
        'taux_occupation': taux_occupation,
        'taux_avancement': taux_avancement,
        'budget_restant': budget_restant,
        'ticket_stats': ticket_stats,
        'ticket_stats_json': ticket_stats_json,
        'role_allocation': role_allocation,
        'total_resources': total_resources,
        'recent_activities': recent_activities,
    }

def get_manager_dashboard_data(user):
    """Calculate and return data for manager dashboard"""
    
    # 1. Projets en cours: Projects with status "En cours" where current user is manager
    projets_en_cours = Project.objects.filter(status='En cours', project_manager=user).count()
    
    # 2. Ressources disponibles: Resources with availability_rate > 50
    ressources_disponibles = Ressource.objects.filter(availability_rate__gt=50).count()
    
    # 3. Tickets ouverts: Tickets with status "Ouvert" created by current user
    tickets_ouverts = Ticket.objects.filter(status='Ouvert', created_by=user).count()
    
    # 4. Taux d'avancement moyen: Average progress of "En cours" projects and tickets
    # Get "En cours" projects where user is manager
    manager_projects = Project.objects.filter(status='En cours', project_manager=user)
    avg_project_progress = manager_projects.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0
    
    # Get "En cours" tickets created by user (tickets don't have progress field, so we'll use a default calculation)
    user_tickets_en_cours = Ticket.objects.filter(status='En cours', created_by=user).count()
    total_user_tickets = Ticket.objects.filter(created_by=user).count()
    
    # Calculate average progress (projects have actual progress, tickets we estimate based on status)
    if manager_projects.exists() and user_tickets_en_cours > 0:
        # Combine project progress with estimated ticket progress (50% for "En cours" tickets)
        ticket_progress_estimate = 50  # "En cours" tickets are considered 50% complete
        total_progress = (avg_project_progress + ticket_progress_estimate) / 2
    elif manager_projects.exists():
        total_progress = avg_project_progress
    elif user_tickets_en_cours > 0:
        total_progress = 50  # Only tickets, estimate 50% for "En cours"
    else:
        total_progress = 0
    
    taux_avancement_moyen = round(total_progress, 1)
    
    # 5. Répartition des tickets par statut: Percentage of ticket statuses for user's created tickets
    user_total_tickets = Ticket.objects.filter(created_by=user).count()
    ticket_stats = {}
    if user_total_tickets > 0:
        user_ticket_counts = Ticket.objects.filter(created_by=user).values('status').annotate(count=Count('status'))
        for item in user_ticket_counts:
            percentage = round((item['count'] / user_total_tickets) * 100, 1)
            ticket_stats[item['status']] = {
                'count': item['count'],
                'percentage': percentage
            }
    
    # Convert ticket stats to JSON for JavaScript
    ticket_stats_json = json.dumps(ticket_stats)
    
    # 6. Équipe: Number of resources per role (all resources in app)
    role_allocation = Ressource.objects.values('role').annotate(count=Count('role')).order_by('-count')
    total_resources = Ressource.objects.count()
    
    # Structure team data for template
    equipe = {
        'total': total_resources,
        'roles': {item['role']: item['count'] for item in role_allocation}
    }
    
    # 7. Projets En Cours: Projects created by user that are "En cours"
    projets_en_cours_list = Project.objects.filter(status='En cours', project_manager=user).select_related('project_manager')
    
    # 8. Activités Récentes: Latest comments and activities from user's projects and tickets
    recent_activities = []
    
    # Get recent project comments from user's managed projects
    user_projects = Project.objects.filter(project_manager=user)
    recent_project_comments = CommentProject.objects.filter(
        project__in=user_projects
    ).select_related('author', 'project').order_by('-created_at')[:5]
    
    for comment in recent_project_comments:
        recent_activities.append({
            'type': 'project_comment',
            'text': f"Nouveau commentaire sur le projet '{comment.project.title}' par {comment.author.first_name} {comment.author.last_name}",
            'author': comment.author,
            'created_at': comment.created_at,
            'related_object': comment.project
        })
    
    # Get recent ticket comments from user's created tickets
    user_tickets = Ticket.objects.filter(created_by=user)
    recent_ticket_comments = CommentTicket.objects.filter(
        ticket__in=user_tickets
    ).select_related('author', 'ticket').order_by('-created_at')[:5]
    
    for comment in recent_ticket_comments:
        recent_activities.append({
            'type': 'ticket_comment',
            'text': f"Nouveau commentaire sur le ticket '{comment.ticket.title}' par {comment.author.first_name} {comment.author.last_name}",
            'author': comment.author,
            'created_at': comment.created_at,
            'related_object': comment.ticket
        })
    
    # Get recent activities from user's projects and tickets
    recent_activity_logs = Activity.objects.filter(
        Q(project__in=user_projects) | Q(ticket__in=user_tickets)
    ).select_related('employee', 'project', 'ticket').order_by('-created_at')[:5]
    
    for activity in recent_activity_logs:
        if activity.project:
            text = f"Activité '{activity.title}' créée sur le projet '{activity.project.title}' par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = activity.project
        elif activity.ticket:
            text = f"Activité '{activity.title}' créée sur le ticket '{activity.ticket.title}' par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = activity.ticket
        else:
            text = f"Activité '{activity.title}' créée par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = None
            
        recent_activities.append({
            'type': 'activity',
            'text': text,
            'author': activity.employee,
            'created_at': activity.created_at,
            'related_object': related_obj
        })
    
    # Sort all activities by creation date and take the most recent 8
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:8]
    
    return {
        'projets_en_cours': projets_en_cours,
        'ressources_disponibles': ressources_disponibles,
        'tickets_ouverts': tickets_ouverts,
        'taux_avancement_moyen': taux_avancement_moyen,
        'repartition_tickets_par_statut': ticket_stats,
        'ticket_stats_json': ticket_stats_json,
        'equipe': equipe,
        'projets_en_cours_list': projets_en_cours_list,
        'activites_recentes': recent_activities,
    }

def get_user_dashboard_data(user):
    """Calculate and return data for user dashboard"""
    
    # 1. Projets en cours: Projects where user is a member and status is "En cours"
    user_projects_en_cours = Project.objects.filter(members=user, status='En cours')
    projets_en_cours = user_projects_en_cours.count()
    
    # 2. Nombres de tickets assignés: Tickets "En cours" where user is assigned or created
    tickets_en_cours = Ticket.objects.filter(
        Q(assigned_to=user) ,
        status='En cours'
    ).distinct().count()
    
    # 3. Tickets Résolus: Tickets with status "Résolu" where user is assigned or created
    tickets_resolus = Ticket.objects.filter(
        Q(assigned_to=user) ,
        status='Résolu'
    ).distinct().count()
    
    # 4. Average Time of resolution: Keep hardcoded for now
    average_resolution_time = "20 jours"
    
    # 5. Répartition des tickets par statut: User's tickets only
    user_tickets = Ticket.objects.filter(
        Q(assigned_to=user)
    ).distinct()
    
    total_user_tickets = user_tickets.count()
    ticket_stats = {}
    if total_user_tickets > 0:
        ticket_counts = user_tickets.values('status').annotate(count=Count('status'))
        for item in ticket_counts:
            percentage = round((item['count'] / total_user_tickets) * 100, 1)
            ticket_stats[item['status']] = {
                'count': item['count'],
                'percentage': percentage
            }
    
    # Convert ticket stats to JSON for JavaScript
    ticket_stats_json = json.dumps(ticket_stats)
    
    # 6. Projets en cours list: Projects "En cours" where user is a member
    projets_en_cours_list = user_projects_en_cours.select_related('project_manager')
    
    # 7. Mes tickets récents: User's tickets ordered by created_at
    recent_tickets = user_tickets.order_by('-created_at')[:10]
    
    # 8. Activités récentes: Comments and Activities from user's projects and tickets
    recent_activities = []
    
    # Get user's projects (where user is member or manager)
    user_all_projects = Project.objects.filter(
        Q(members=user) 
    ).distinct()
    
    # Get recent project comments from user's projects
    recent_project_comments = CommentProject.objects.filter(
        project__in=user_all_projects
    ).select_related('author', 'project').order_by('-created_at')[:5]
    
    for comment in recent_project_comments:
        recent_activities.append({
            'type': 'project_comment',
            'text': f"Nouveau commentaire sur le projet '{comment.project.title}' par {comment.author.first_name} {comment.author.last_name}",
            'author': comment.author,
            'created_at': comment.created_at,
            'related_object': comment.project
        })
    
    # Get recent ticket comments from user's tickets
    recent_ticket_comments = CommentTicket.objects.filter(
        ticket__in=user_tickets
    ).select_related('author', 'ticket').order_by('-created_at')[:5]
    
    for comment in recent_ticket_comments:
        recent_activities.append({
            'type': 'ticket_comment',
            'text': f"Nouveau commentaire sur le ticket '{comment.ticket.title}' par {comment.author.first_name} {comment.author.last_name}",
            'author': comment.author,
            'created_at': comment.created_at,
            'related_object': comment.ticket
        })
    
    # Get recent activities from user's projects and tickets
    recent_activity_logs = Activity.objects.filter(
        Q(project__in=user_all_projects) | Q(ticket__in=user_tickets)
    ).select_related('employee', 'project', 'ticket').order_by('-created_at')[:5]
    
    for activity in recent_activity_logs:
        if activity.project:
            text = f"Activité '{activity.title}' créée sur le projet '{activity.project.title}' par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = activity.project
        elif activity.ticket:
            text = f"Activité '{activity.title}' créée sur le ticket '{activity.ticket.title}' par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = activity.ticket
        else:
            text = f"Activité '{activity.title}' créée par {activity.employee.first_name} {activity.employee.last_name}"
            related_obj = None
            
        recent_activities.append({
            'type': 'activity',
            'text': text,
            'author': activity.employee,
            'created_at': activity.created_at,
            'related_object': related_obj
        })
    
    # Sort all activities by creation date and take the most recent 8
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:8]
    
    return {
        'projets_en_cours': projets_en_cours,
        'tickets_en_cours': tickets_en_cours,
        'tickets_resolus': tickets_resolus,
        'average_resolution_time': average_resolution_time,
        'ticket_stats': ticket_stats,
        'ticket_stats_json': ticket_stats_json,
        'projets_en_cours_list': projets_en_cours_list,
        'mes_tickets_recents': recent_tickets,
        'recent_activities': recent_activities,
    }