from django.shortcuts import render, redirect, get_object_or_404
from .models import Ressource
from activities.models import Activity  # Ajouter cet import
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
import pandas as pd
from urllib.parse import quote
from datetime import datetime
import json  # Ajouter cet import
from django.http import JsonResponse

@login_required
def ressources(request):
    user = request.user
    
    # Filter resources based on user role
    if user.appRole == 'ADMIN':
        # Admin sees all resources
        ressources = Ressource.objects.all()
    elif user.appRole == 'MANAGER':
        # Manager sees resources from their projects + themselves
        from projects.models import Project
        managed_projects = Project.objects.filter(project_manager=user)
        # Use Q objects to combine conditions properly
        ressources = Ressource.objects.filter(
            Q(members__in=managed_projects) | Q(id=user.id)
        ).distinct()
    else:
        # Regular user sees only resources from their projects + themselves
        user_projects = user.members.all()
        # Use Q objects to combine conditions properly
        ressources = Ressource.objects.filter(
            Q(members__in=user_projects) | Q(id=user.id)
        ).distinct()

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Split the search query into words to search for each word in skills
        search_terms = search_query.split()
        
        # Start with an empty Q object
        query = Q()
        
        # Add conditions for each search term
        for term in search_terms:
            # Search in individual fields
            query |= Q(first_name__icontains=term)
            query |= Q(last_name__icontains=term)
            query |= Q(skills__icontains=term)
            query |= Q(email__icontains=term)
            query |= Q(role__icontains=term)
            query |= Q(status__icontains=term)
        
        # Also search for the full query in case it's a complete name or phrase
        query |= Q(first_name__icontains=search_query)
        query |= Q(last_name__icontains=search_query)
        # Search for full name (first_name + space + last_name)
        ressources_ids = []
        for r in ressources:
            full_name = f"{r.first_name} {r.last_name}".lower()
            if search_query.lower() in full_name:
                ressources_ids.append(r.id)
        
        # Combine all conditions
        ressources = ressources.filter(query | Q(id__in=ressources_ids))

    # Filtering functionality
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    if role_filter:
        ressources = ressources.filter(role=role_filter)
    if status_filter:
        ressources = ressources.filter(status=status_filter)

    # Get unique roles and statuses for filter dropdowns
    roles = Ressource.objects.values_list('role', flat=True).distinct()
    statuses = Ressource.objects.values_list('status', flat=True).distinct()

    return render(request, 'ressources.html', {
        'ressources': ressources,
        'roles': roles,
        'statuses': statuses,
        'current_role': role_filter,
        'current_status': status_filter,
        'search_query': search_query,
        'user_role': user.appRole
    })


@login_required
def ressourcesDetails(request, resource_id=None):
    if resource_id:
        try:
            resource = get_object_or_404(Ressource, id=resource_id)
            user = request.user
            
            # Vérifier les permissions d'accès selon le rôle
            if user.appRole == 'ADMIN':
                # Admin peut voir toutes les ressources
                pass
            elif user.appRole == 'MANAGER':
                # Manager peut voir les ressources de ses projets + lui-même
                from projects.models import Project
                managed_projects = Project.objects.filter(project_manager=user)
                if not (resource.members.filter(id__in=managed_projects).exists() or resource.id == user.id):
                    return redirect('ressources')
            else:
                # Utilisateur normal peut voir seulement les ressources de ses projets + lui-même
                user_projects = user.members.all()
                if not (resource.members.filter(id__in=user_projects).exists() or resource.id == user.id):
                    return redirect('ressources')
            
            # Récupérer les tickets assignés à cette ressource
            assigned_tickets = resource.assignedTickets.all()
            
            # Récupérer les projets où cette ressource est membre
            assigned_projects = resource.members.all()
            
            # Récupérer les activités de cette ressource pour le calendrier
            activities = Activity.objects.filter(employee=resource)
            
            # Préparer les événements du calendrier
            calendar_events = []
            for activity in activities:
                event_name = activity.title
                if activity.project:
                    event_name = activity.project.title
                elif activity.ticket:
                    event_name = activity.ticket.title
                
                # Déterminer le statut
                now = datetime.now().date()
                activity_date = activity.start_datetime.date()
                
                if activity_date < now:
                    status = 'completed'
                elif activity_date == now:
                    status = 'inprogress'
                else:
                    status = 'planned'
                
                calendar_events.append({
                    'date': activity.start_datetime.strftime('%Y-%m-%d'),
                    'name': event_name,
                    'status': status
                })
            
            # Calculer les KPI
            completed_tickets = assigned_tickets.filter(status='Fermé').count()
            total_tickets = assigned_tickets.count()
            completed_projects = assigned_projects.filter(status='Terminé').count()
            
            return render(request, 'ressourcesDetails.html', {
                'resource': resource,
                'ressource': resource,
                'assigned_tickets': assigned_tickets,
                'assigned_projects': assigned_projects,
                'completed_tickets': completed_tickets,
                'total_tickets': total_tickets,
                'completed_projects': completed_projects,
                'calendar_events': json.dumps(calendar_events),
            })
        except Ressource.DoesNotExist:
            return redirect('/ressources/')
    return redirect('/ressources/')  # Rediriger si pas d'ID


def add_resource(request):
    # Vérifier que l'utilisateur a les permissions
    if request.user.appRole not in ['ADMIN', 'MANAGER']:
        return redirect('ressources')
    
    if request.method == 'POST':
        first_name = request.POST.get('name')
        last_name = ''  # À adapter si tu veux le demander
        email = request.POST.get('email')
        role = request.POST.get('role')
        status = request.POST.get('status')
        phone_number = request.POST.get('phone')
        entry_date = request.POST.get('entry_date')
        location = request.POST.get('location')
        availability_rate = request.POST.get('availability')
        skills = request.POST.get('skills')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return render(request, 'add_resource.html', {'error': 'Les mots de passe ne correspondent pas'})
        username = email
        app_role = request.POST.get('appRole')
        
        # Traitement de la date d'entrée
        parsed_entry_date = None
        if entry_date:
            try:
                parsed_entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            except ValueError:
                return render(request, 'add_resource.html', {'error': 'Format de date invalide. Utilisez le format YYYY-MM-DD.'})
        
        try:
            user = Ressource.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                status=status,
                phone_number=phone_number,
                entry_date=parsed_entry_date,
                location=location,
                availability_rate=availability_rate,
                skills=skills,
                appRole=app_role
            )
            return redirect('/ressources/')
        except Exception as e:
            return render(request, 'add_resource.html', {'error': f'Erreur lors de la création: {str(e)}'})
    return render(request, 'add_resource.html')


@login_required
def edit_resource(request, resource_id):
    # Vérifier que l'utilisateur a les permissions
    if request.user.appRole not in ['ADMIN', 'MANAGER']:
        return redirect('ressources')
        
    resource = get_object_or_404(Ressource, id=resource_id)
    
    # Vérifier que le manager peut seulement éditer les ressources de ses projets
    if request.user.appRole == 'MANAGER':
        from projects.models import Project
        managed_projects = Project.objects.filter(project_manager=request.user)
        if not resource.members.filter(id__in=managed_projects).exists():
            return redirect('ressources')
    
    if request.method == 'POST':
        first_name = request.POST.get('name')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        role = request.POST.get('role')
        status = request.POST.get('status')
        phone_number = request.POST.get('phone')
        entry_date = request.POST.get('entry_date')
        location = request.POST.get('location')
        availability_rate = request.POST.get('availability')
        skills = request.POST.get('skills')
        app_role = request.POST.get('appRole')
        
        # Mise à jour des champs
        resource.first_name = first_name
        resource.last_name = last_name
        resource.email = email
        resource.role = role
        resource.status = status
        resource.phone_number = phone_number
        # Vérifier si entry_date est vide et le gérer correctement
        if entry_date:
            try:
                resource.entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            except ValueError:
                return render(request, 'edit_resource.html', {'resource': resource, 'error': 'Format de date invalide. Utilisez le format YYYY-MM-DD.'})
        resource.location = location
        resource.availability_rate = availability_rate
        resource.skills = skills
        resource.appRole = app_role
        
        # Vérifier si un nouveau mot de passe est fourni
        password = request.POST.get('password')
        if password:
            confirm_password = request.POST.get('confirm_password')
            if password != confirm_password:
                return render(request, 'edit_resource.html', {'resource': resource, 'error': 'Les mots de passe ne correspondent pas'})
            resource.set_password(password)
        
        resource.save()
        return redirect('/ressources/')
    
    return render(request, 'edit_resource.html', {'resource': resource})


def delete_resource(request, resource_id):
    if request.method == 'POST':
        resource = Ressource.objects.get(id=resource_id)
        resource.delete()
        return redirect('/ressources/')
    return redirect('/ressources/')


def export_ressources_excel(request):
    ressources = Ressource.objects.all()
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Split the search query into words to search for each word in skills
        search_terms = search_query.split()
        
        # Start with an empty Q object
        query = Q()
        
        # Add conditions for each search term
        for term in search_terms:
            # Search in individual fields
            query |= Q(first_name__icontains=term)
            query |= Q(last_name__icontains=term)
            query |= Q(skills__icontains=term)
            query |= Q(email__icontains=term)
            query |= Q(role__icontains=term)
            query |= Q(status__icontains=term)
        
        # Also search for the full query in case it's a complete name or phrase
        query |= Q(first_name__icontains=search_query)
        query |= Q(last_name__icontains=search_query)
        # Search for full name (first_name + space + last_name)
        ressources_ids = []
        for r in ressources:
            full_name = f"{r.first_name} {r.last_name}".lower()
            if search_query.lower() in full_name:
                ressources_ids.append(r.id)
        
        # Combine all conditions
        ressources = ressources.filter(query | Q(id__in=ressources_ids))
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    if role_filter:
        ressources = ressources.filter(role=role_filter)
    if status_filter:
        ressources = ressources.filter(status=status_filter)
    data = list(ressources.values('first_name','last_name','email','role','status','phone_number','entry_date','location','availability_rate','skills'))
    df = pd.DataFrame(data)
    filename = request.GET.get('filename')
    if not filename:
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"ressources_{date_str}.xlsx"
    else:
        filename = f"{filename}.xlsx"
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{quote(filename)}"
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ressources')
    return response


@login_required
def get_resource_activities(request, resource_id):
    """API endpoint to get activities for a specific resource"""
    try:
        resource = get_object_or_404(Ressource, id=resource_id)
        
        # Get activities for this resource
        activities = Activity.objects.filter(employee=resource).order_by('start_datetime')
        
        activities_data = []
        for activity in activities:
            # Determine activity name
            activity_name = activity.title
            if activity.project:
                activity_name = f"{activity.project.title} - {activity.title}"
            elif activity.ticket:
                activity_name = f"Ticket #{activity.ticket.id} - {activity.title}"
            
            # Determine status based on dates
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
                'title': activity_name,
                'description': activity.description,
                'start': activity.start_datetime.isoformat(),
                'end': activity.end_datetime.isoformat(),
                'status': status,
                'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
                'project': activity.project.title if activity.project else None,
                'ticket': activity.ticket.id if activity.ticket else None
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
