from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from projects.models import Project, CommentProject, ProjectStatusLog
from ressources.models import Ressource
from tickets.models import Ticket, CommentTicket, TicketStatusLog
from activities.models import Activity
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
import json
import calendar

def get_active_tickets_count_at_date(target_date, user=None):
    """Count tickets that were active (Ouvert or En cours) at a specific date"""
    # Get all tickets that existed at the target date
    if user:
        tickets = Ticket.objects.filter(
            created_at__lte=target_date,
            created_by=user
        )
    else:
        tickets = Ticket.objects.filter(
            created_at__lte=target_date
        )
    
    active_count = 0
    
    for ticket in tickets:
        # Get the latest status log for this ticket up to the target date
        latest_log = TicketStatusLog.objects.filter(
            ticket=ticket,
            timestamp__lte=target_date
        ).order_by('-timestamp').first()
        
        # If there's a status log and it's active status, count it
        if latest_log and latest_log.status in ['Ouvert', 'En cours']:
            active_count += 1
    
    return active_count

def get_active_projects_count_at_date(target_date, user=None):
    """Count projects that were active (À initier or En cours) at a specific date"""
    # Get all projects that existed at the target date
    if user:
        projects = Project.objects.filter(
            created_at__lte=target_date,
            project_manager=user
        )
    else:
        projects = Project.objects.filter(
            created_at__lte=target_date
        )
    
    active_count = 0
    
    for project in projects:
        # Get the latest status log for this project up to the target date
        latest_log = ProjectStatusLog.objects.filter(
            project=project,
            timestamp__lte=target_date
        ).order_by('-timestamp').first()
        
        # If there's a status log and it's active status, count it
        if latest_log and latest_log.status in ['À initier', 'En cours']:
            active_count += 1
    
    return active_count

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

def get_ticket_curve_data(user=None, period='month'):
    """Generate active tickets evolution curve data (Ouvert + En cours only)"""
    end_date = timezone.now()
    
    # Determine date range and grouping based on period
    if period == 'month':
        start_date = end_date - timedelta(days=30)
        date_format = '%Y-%m-%d'
        label_format = '%d'
    elif period == 'year':
        # Always show last 12 months, even if no data exists
        start_date = end_date - timedelta(days=365)
        date_format = '%Y-%m'
        label_format = '%b %Y'
    else:  # all_time
        # Get the earliest ticket creation date, but ensure at least 12 months
        if user:
            earliest_ticket = TicketStatusLog.objects.filter(
                ticket__created_by=user
            ).order_by('timestamp').first()
        else:
            earliest_ticket = TicketStatusLog.objects.order_by('timestamp').first()
        
        if earliest_ticket:
            earliest_date = earliest_ticket.timestamp
            # Ensure we show at least 12 months of data
            min_start_date = end_date - timedelta(days=365)
            start_date = min(earliest_date, min_start_date)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Determine if we should group by month or year based on time span
        days_span = (end_date - start_date).days
        if days_span > 730:  # More than 2 years, group by year
            date_format = '%Y'
            label_format = '%Y'
        else:  # Less than 2 years, group by month
            date_format = '%Y-%m'
            label_format = '%b %Y'
    
    # Generate labels and data arrays
    labels = []
    active_values = []
    
    if period == 'month':
        # Generate daily labels for the last 30 days
        for i in range(29, -1, -1):
            date = end_date - timedelta(days=i)
            date_key = date.strftime(date_format)
            label = date.strftime(label_format)
            
            # Count active tickets at this date
            active_count = get_active_tickets_count_at_date(date, user)
            
            labels.append(label)
            active_values.append(active_count)
    elif period == 'year':
        # Generate monthly labels for the last 12 months
        for i in range(11, -1, -1):
            date = end_date - timedelta(days=i*30)
            date_key = date.strftime(date_format)
            label = date.strftime(label_format)
            
            # Count active tickets at this date
            active_count = get_active_tickets_count_at_date(date, user)
            
            labels.append(label)
            active_values.append(active_count)
    else:  # all_time
        # Generate labels based on time span and format
        if date_format == '%Y':  # Yearly format
            start_year = start_date.year
            end_year = end_date.year
            for year in range(start_year, end_year + 1):
                date_key = str(year)
                date = datetime(year, 12, 31, tzinfo=timezone.get_current_timezone())
                
                # Count active tickets at this date
                active_count = get_active_tickets_count_at_date(date, user)
                
                labels.append(date_key)
                active_values.append(active_count)
        else:  # Monthly format
            current_date = start_date.replace(day=1)  # Start from first day of month
            while current_date <= end_date:
                date_key = current_date.strftime(date_format)
                label = current_date.strftime(label_format)
                
                # Count active tickets at end of this month
                if current_date.month == 12:
                    end_of_month = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1, day=1)
                    end_of_month = next_month - timedelta(days=1)
                
                active_count = get_active_tickets_count_at_date(end_of_month, user)
                
                labels.append(label)
                active_values.append(active_count)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
    
    return {
        'labels': labels,
        'created_data': active_values,  # Keep same key for compatibility
        'resolved_data': [0] * len(active_values)  # Empty array for compatibility
    }

def get_project_curve_data(user=None, period='month'):
    """Generate active projects evolution curve data (À initier + En cours only)"""
    end_date = timezone.now()
    
    # Determine date range and grouping based on period
    if period == 'month':
        start_date = end_date - timedelta(days=30)
        date_format = '%Y-%m-%d'
        label_format = '%d'
    elif period == 'year':
        # Always show last 12 months, even if no data exists
        start_date = end_date - timedelta(days=365)
        date_format = '%Y-%m'
        label_format = '%b %Y'
    else:  # all_time
        # Get the earliest project creation date, but ensure at least 12 months
        if user:
            earliest_project = ProjectStatusLog.objects.filter(
                project__project_manager=user
            ).order_by('timestamp').first()
        else:
            earliest_project = ProjectStatusLog.objects.order_by('timestamp').first()
        
        if earliest_project:
            earliest_date = earliest_project.timestamp
            # Ensure we show at least 12 months of data
            min_start_date = end_date - timedelta(days=365)
            start_date = min(earliest_date, min_start_date)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Determine if we should group by month or year based on time span
        days_span = (end_date - start_date).days
        if days_span > 730:  # More than 2 years, group by year
            date_format = '%Y'
            label_format = '%Y'
        else:  # Less than 2 years, group by month
            date_format = '%Y-%m'
            label_format = '%b %Y'
    
    # Generate labels and data arrays
    labels = []
    active_values = []
    
    if period == 'month':
        # Generate daily labels for the last 30 days
        for i in range(29, -1, -1):
            date = end_date - timedelta(days=i)
            date_key = date.strftime(date_format)
            label = date.strftime(label_format)
            
            # Count active projects at this date
            active_count = get_active_projects_count_at_date(date, user)
            
            labels.append(label)
            active_values.append(active_count)
    elif period == 'year':
        # Generate monthly labels for the last 12 months
        for i in range(11, -1, -1):
            date = end_date - timedelta(days=i*30)
            date_key = date.strftime(date_format)
            label = date.strftime(label_format)
            
            # Count active projects at this date
            active_count = get_active_projects_count_at_date(date, user)
            
            labels.append(label)
            active_values.append(active_count)
    else:  # all_time
        # Generate labels based on time span and format
        if date_format == '%Y':  # Yearly format
            start_year = start_date.year
            end_year = end_date.year
            for year in range(start_year, end_year + 1):
                date_key = str(year)
                date = datetime(year, 12, 31, tzinfo=timezone.get_current_timezone())
                
                # Count active projects at this date
                active_count = get_active_projects_count_at_date(date, user)
                
                labels.append(date_key)
                active_values.append(active_count)
        else:  # Monthly format
            current_date = start_date.replace(day=1)  # Start from first day of month
            while current_date <= end_date:
                date_key = current_date.strftime(date_format)
                label = current_date.strftime(label_format)
                
                # Count active projects at end of this month
                if current_date.month == 12:
                    end_of_month = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1, day=1)
                    end_of_month = next_month - timedelta(days=1)
                
                active_count = get_active_projects_count_at_date(end_of_month, user)
                
                labels.append(label)
                active_values.append(active_count)
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
    
    return {
        'labels': labels,
        'created_data': active_values,  # Keep same key for compatibility
        'finished_data': [0] * len(active_values)  # Empty array for compatibility
    }

def get_admin_dashboard_data():
    """Calculate and return data for admin dashboard"""
    
    # 1. Projets en cours: Projects with status "En cours"
    projets_en_cours = Project.objects.filter(status='En cours').count()
    
    # 2. Taux de disponibilité des ressources: Average of all resources availability_rate
    avg_availability = Ressource.objects.filter(availability_rate__isnull=False).aggregate(
        avg_rate=Avg('availability_rate')
    )['avg_rate'] or 0
    taux_disponibilite = round(avg_availability, 1)
    
    # 3. Taux d'avancement des projets: Average progress of "En cours" projects
    avg_progress = Project.objects.filter(status='En cours').aggregate(
        avg_progress=Avg('progress')
    )['avg_progress'] or 0
    taux_avancement = round(avg_progress, 1)
    
    # 4. Total des ressources: Count of all resources in the system
    total_ressources = Ressource.objects.count()
    
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
    
    # 8. Get ticket curve data for charts (all periods)
    ticket_curve_month = get_ticket_curve_data(period='month')
    ticket_curve_year = get_ticket_curve_data(period='year')
    ticket_curve_all = get_ticket_curve_data(period='all_time')
    
    # 9. Get project curve data for charts (all periods)
    project_curve_month = get_project_curve_data(period='month')
    project_curve_year = get_project_curve_data(period='year')
    project_curve_all = get_project_curve_data(period='all_time')
    
    return {
        'projets_en_cours': projets_en_cours,
        'taux_occupation': taux_disponibilite,
        'taux_avancement': taux_avancement,
        'total_ressources': total_ressources,
        'ticket_stats': ticket_stats,
        'ticket_stats_json': ticket_stats_json,
        'role_allocation': role_allocation,
        'total_resources': total_resources,
        'recent_activities': recent_activities,
        'ticket_curve_month': json.dumps(ticket_curve_month),
        'ticket_curve_year': json.dumps(ticket_curve_year),
        'ticket_curve_all': json.dumps(ticket_curve_all),
        'project_curve_month': json.dumps(project_curve_month),
        'project_curve_year': json.dumps(project_curve_year),
        'project_curve_all': json.dumps(project_curve_all),
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
    
    # 9. Get ticket curve data for manager's tickets (all periods)
    ticket_curve_month = get_ticket_curve_data(user=user, period='month')
    ticket_curve_year = get_ticket_curve_data(user=user, period='year')
    ticket_curve_all = get_ticket_curve_data(user=user, period='all_time')
    
    # 10. Get project curve data for manager's projects (all periods)
    project_curve_month = get_project_curve_data(user=user, period='month')
    project_curve_year = get_project_curve_data(user=user, period='year')
    project_curve_all = get_project_curve_data(user=user, period='all_time')
    
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
        'ticket_curve_month': json.dumps(ticket_curve_month),
        'ticket_curve_year': json.dumps(ticket_curve_year),
        'ticket_curve_all': json.dumps(ticket_curve_all),
        'project_curve_month': json.dumps(project_curve_month),
        'project_curve_year': json.dumps(project_curve_year),
        'project_curve_all': json.dumps(project_curve_all),
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