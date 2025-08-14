from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Project, Tag, CommentProject
from .forms import ProjectForm
from ressources.models import Ressource
from tickets.models import Ticket
from django.db.models import Q

@login_required
def projects(request):
    user = request.user
    
    # Filter projects based on user role
    if user.appRole == 'ADMIN':
        # Admin sees all projects
        projects = Project.objects.all()
    elif user.appRole == 'MANAGER':
        # Manager sees projects where they are the project manager
        projects = Project.objects.filter(project_manager=user)
    else:
        # Regular user sees projects where they are a member
        projects = Project.objects.filter(members=user)
    
    # Filtrer les projets avec des IDs valides
    projects = projects.exclude(id__isnull=True)
    
    # Apply search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply additional filters from query parameters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    project_manager_filter = request.GET.get('project_manager')
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    
    if project_manager_filter:
        projects = projects.filter(project_manager=project_manager_filter)
    
    # Get filter options for dropdowns
    status_choices = Project._meta.get_field('status').choices
    priority_choices = Project._meta.get_field('priority').choices
    project_managers = Ressource.objects.filter(appRole__in=['ADMIN', 'MANAGER'])
    
    # Check if user can create projects (admin or manager)
    can_create_project = user.appRole in ['ADMIN', 'MANAGER']
    
    return render(request, 'projects.html', {
        'projects': projects,
        'can_create_project': can_create_project,
        'user_role': user.appRole,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'project_managers': project_managers,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_project_manager': project_manager_filter,
        'search_query': search_query  # Add this line
    })


@login_required
def create_project(request):
    if request.user.appRole not in ['ADMIN', 'MANAGER']:
        return redirect('projects')
        
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            
            # Assigner automatiquement le créateur comme chef de projet si aucun n'est spécifié
            if not project.project_manager:
                project.project_manager = request.user
            
            # Set start date to None initially
            project.start_date = None
            project.end_date = None
            project.save()
            
            # Save the many-to-many relationships
            form.save_m2m()
            
            # Add members from the form
            members = form.cleaned_data.get('members')
            if members:
                project.members.set(members)
            
            # Si aucun membre n'est spécifié, ajouter le créateur comme membre
            if not members:
                project.members.add(request.user)
            
            return redirect('projects')
        else:
            # Debug: afficher les erreurs de validation
            print("Erreurs de validation du formulaire:")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
    else:
        form = ProjectForm()
    
    # Récupérer tous les membres disponibles de la base de données
    available_members = Ressource.objects.all().order_by('first_name', 'last_name')
    
    return render(request, 'project_form.html', {
        'form': form,
        'available_members': available_members
    })

@login_required
def projectDetails(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Check if user is admin or project manager
    user = request.user
    can_edit = user.appRole == 'ADMIN' or (user.appRole == 'MANAGER' and project.project_manager == user)
    return render(request, 'projectInfo.html', {'project': project, 'pk': pk, 'active_tab': 'info', 'can_edit': can_edit})


@login_required
def projectMembers(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Get all members of the project
    members = project.members.all()
    # Get additional information for each member
    members_info = []
    for member in members:
        member_info = {
            'id': member.id,
            'name': f"{member.first_name} {member.last_name}",
            'role': member.role,
            'skills': member.skills.split(',') if member.skills else [],
            'email': member.email,
            'phone': member.phone_number,
            'status': member.status,
            'location': member.location
        }
        members_info.append(member_info)
    
    # Check if user is admin or project manager
    user = request.user
    can_edit = user.appRole == 'ADMIN' or (user.appRole == 'MANAGER' and project.project_manager == user)
    
    return render(request, 'projectMembers.html', {
        'project': project, 
        'pk': pk, 
        'active_tab': 'membres',
        'members': members_info,
        'can_edit': can_edit
    })

@login_required
def projectCalendar(request, pk):
    from datetime import datetime, timedelta
    import calendar
    
    project = get_object_or_404(Project, pk=pk)
    
    # Get current month and year
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Get all activities for this project in the current month
    from activities.models import Activity
    activities = Activity.objects.filter(
        project=project,
        start_datetime__year=current_year,
        start_datetime__month=current_month
    ).order_by('start_datetime')
    
    # Get project members for color assignment
    project_members = list(project.members.all())
    member_colors = {}
    
    # Define a set of distinct colors for members
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
    ]
    
    for i, member in enumerate(project_members):
        member_colors[member.id] = colors[i % len(colors)]
    
    # Format activities for the calendar
    calendar_activities = []
    for activity in activities:
        calendar_activities.append({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'start_date': activity.start_datetime,  # Garder l'objet datetime complet
            'end_date': activity.end_datetime,      # Garder l'objet datetime complet
            'type': activity.activity_type,  # Ajouter le type d'activité
            'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
            'employee_id': activity.employee.id,
            'employee_color': member_colors.get(activity.employee.id, '#A08D80'),  # Default color
            'charge': float(activity.charge) if activity.charge else 0  # Convertir en float
        })
    
    # Get calendar information for the current month
    cal = calendar.monthcalendar(current_year, current_month)
    
    # Noms des mois en français
    mois_francais = [
        '', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ]
    month_name = mois_francais[current_month]
    
    # Check if user is admin or project manager
    user = request.user
    can_edit = user.appRole == 'ADMIN' or (user.appRole == 'MANAGER' and project.project_manager == user)
    
    return render(request, 'projectCalendar.html', {
        'project': project, 
        'pk': pk, 
        'active_tab': 'calendrier',
        'calendar_activities': calendar_activities,
        'calendar_data': cal,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': month_name,
        'can_edit': can_edit,
        'project_members': project_members,
        'member_colors': member_colors
    })


@login_required
def search_tags(request):
    """API endpoint to search for tags"""
    term = request.GET.get('term', '')
    if len(term) < 2:
        return JsonResponse({'tags': []})
    
    tags = Tag.objects.filter(name__icontains=term)[:10]
    tags_data = [{'id': tag.id, 'name': tag.name} for tag in tags]
    
    return JsonResponse({'tags': tags_data})


@login_required
@require_POST
def create_tag(request):
    """API endpoint to create a new tag"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Tag name is required'})
        
        # Check if tag already exists
        tag, created = Tag.objects.get_or_create(name=name)
        
        return JsonResponse({
            'success': True,
            'tag': {
                'id': tag.id,
                'name': tag.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_all_tags(request):
    """API endpoint to get all available tags"""
    tags = Tag.objects.all().order_by('name')
    tags_data = [{'id': tag.id, 'name': tag.name} for tag in tags]
    return JsonResponse({'tags': tags_data})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check permissions
    user = request.user
    if user.appRole not in ['ADMIN', 'MANAGER'] or (user.appRole == 'MANAGER' and project.project_manager != user):
        return redirect('projects')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            
            # Sauvegarder les relations many-to-many
            form.save_m2m()
            
            # Gérer les membres spécifiquement
            members = form.cleaned_data.get('members')
            if members:
                project.members.set(members)
            else:
                project.members.clear()
                
            # Gérer les tags spécifiquement
            tags = form.cleaned_data.get('tags')
            if tags:
                project.tags.set(tags)
            else:
                project.tags.clear()
            
            return redirect('projectDetails', pk=pk)
    else:
        form = ProjectForm(instance=project)
    
    # Récupérer tous les membres disponibles
    available_members = Ressource.objects.all().order_by('first_name', 'last_name')
    
    return render(request, 'project_form.html', {
        'form': form, 
        'project': project, 
        'edit_mode': True,
        'available_members': available_members
    })


@login_required
def projectComments(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    
    # Check if user has permission to view the project
    if not (user.appRole == 'ADMIN' or user.appRole == 'MANAGER' or user in project.members.all()):
        return redirect('projects')
    
    # Check if user has permission to edit the project
    can_edit = user.appRole == 'ADMIN' or (user.appRole == 'MANAGER' and project.project_manager == user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment = CommentProject.objects.create(
                content=content,
                author=user,
                project=project
            )
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.utils.timesince import timesince
                from django.utils import timezone
                
                # Return JSON response
                return JsonResponse({
                    'success': True,
                    'content': comment.content,
                    'author_name': comment.author.get_full_name() or comment.author.username,
                    'author_initials': ''.join([name[0].upper() for name in (comment.author.first_name, comment.author.last_name) if name]),
                    'author_role': comment.author.appRole,
                    'created_at': timezone.localtime(comment.created_at).strftime('%d %b %Y, %H:%M')
                })
            
            # Regular form submission - redirect to avoid form resubmission
            return redirect('projectComments', pk=pk)
    
    # Get all comments for this project ordered by creation date
    comments = CommentProject.objects.filter(project=project).order_by('created_at')
    
    return render(request, 'projectComments.html', {
        'project': project,
        'comments': comments,
        'can_edit': can_edit,
        'active_tab': 'commentaires',
        'pk': pk
    })


@login_required
def delete_project(request, pk):
    # Vérifier que l'utilisateur est admin
    if request.user.appRole != 'ADMIN':
        return redirect('projects')
    
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.delete()
        return redirect('projects')
    
    return render(request, 'delete_project.html', {'project': project})


@login_required
def global_search(request):
    """
    Global search function that searches across Projects, Resources, and Tickets
    Returns JSON response with search results for dropdown suggestions
    """
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    user = request.user
    results = []
    
    # Search Projects
    if user.appRole == 'ADMIN':
        projects = Project.objects.all()
    elif user.appRole == 'MANAGER':
        projects = Project.objects.filter(project_manager=user)
    else:
        projects = Project.objects.filter(members=user)
    
    project_results = projects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    )[:5]  # Limit to 5 results
    
    for project in project_results:
        results.append({
            'type': 'project',
            'id': project.id,
            'title': project.title,
            'description': project.description[:100] + '...' if len(project.description) > 100 else project.description,
            'url': f'/projects/details/{project.id}/',
            'status': project.status,
            'priority': project.priority
        })
    
    # Search Resources
    resource_results = Ressource.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(role__icontains=query) |
        Q(skills__icontains=query)
    )[:5]  # Limit to 5 results
    
    for resource in resource_results:
        results.append({
            'type': 'resource',
            'id': resource.id,
            'title': f'{resource.first_name} {resource.last_name}',
            'description': f'{resource.role} - {resource.skills[:50]}...' if resource.skills and len(resource.skills) > 50 else resource.role,
            'url': f'/ressources/details/{resource.id}/',
            'status': resource.status,
            'role': resource.role
        })
    
    # Search Tickets
    if user.appRole == 'ADMIN':
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        )
    
    ticket_results = tickets.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    )[:5]  # Limit to 5 results
    
    for ticket in ticket_results:
        results.append({
            'type': 'ticket',
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description[:100] + '...' if len(ticket.description) > 100 else ticket.description,
            'url': f'/tickets/details/{ticket.id}/',
            'status': ticket.status,
            'priority': ticket.priority
        })
    
    return JsonResponse({
        'results': results,
        'total_count': len(results)
    })


@login_required
def get_user_projects_api(request):
    """API endpoint pour récupérer les projets de l'utilisateur connecté"""
    user = request.user
    
    # Filtrer les projets selon le rôle de l'utilisateur
    if user.appRole == 'ADMIN':
        # Admin voit tous les projets
        projects = Project.objects.all()
    elif user.appRole == 'MANAGER':
        # Manager voit les projets qu'il gère
        projects = Project.objects.filter(project_manager=user)
    else:
        # Utilisateur normal voit les projets où il est membre
        projects = Project.objects.filter(members=user)
    
    projects_data = [{
        'id': project.id,
        'name': project.title,
        'title': project.title
    } for project in projects]
    
    return JsonResponse(projects_data, safe=False)


@login_required
def get_project_activities(request, pk):
    from django.http import JsonResponse
    from activities.models import Activity
    from datetime import datetime
    import json
    
    project = get_object_or_404(Project, pk=pk)
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    activities = Activity.objects.filter(
        project=project,
        start_datetime__year=year,
        start_datetime__month=month
    ).order_by('start_datetime')
    
    # Get project members for color assignment
    project_members = list(project.members.all())
    member_colors = {}
    
    # Define a set of distinct colors for members
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
    ]
    
    for i, member in enumerate(project_members):
        member_colors[member.id] = colors[i % len(colors)]
    
    activities_data = []
    for activity in activities:
        activities_data.append({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'start_datetime': activity.start_datetime.isoformat(),
            'end_datetime': activity.end_datetime.isoformat(),
            # Ajouter les propriétés attendues par le frontend
            'startDate': activity.start_datetime.isoformat(),
            'endDate': activity.end_datetime.isoformat(),
            'start_date': activity.start_datetime.isoformat(),
            'end_date': activity.end_datetime.isoformat(),
            'type': activity.activity_type,
            'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
            'employee_id': activity.employee.id,
            'employee_color': member_colors.get(activity.employee.id, '#A08D80'),
            'charge': float(activity.charge) if activity.charge else 0
        })
    
    return JsonResponse({
        'success': True,
        'activities': activities_data
    })


@login_required
@require_POST
def create_project_activity(request, pk):
    """Créer une activité pour un projet spécifique"""
    try:
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        
        # Vérifier que l'utilisateur est membre du projet ou manager/admin
        if not (user.appRole in ['ADMIN', 'MANAGER'] or project.members.filter(id=user.id).exists()):
            return JsonResponse({
                'success': False,
                'message': 'Vous n\'êtes pas autorisé à créer une activité pour ce projet'
            }, status=403)
        
        data = json.loads(request.body)
        
        # Importer Activity ici pour éviter les imports circulaires
        from activities.models import Activity
        from datetime import datetime
        
        # Créer l'activité
        activity = Activity(
            title=data['title'],
            description=data.get('description', ''),
            employee=user,
            activity_type=data.get('activity_type', 'PROJECT'),
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime']),
            project=project
        )
        
        # Si l'utilisateur a sélectionné une autre ressource liée
        if data.get('ticket_id') and data.get('activity_type') == 'TICKET':
            from tickets.models import Ticket
            ticket = get_object_or_404(Ticket, id=data['ticket_id'])
            activity.ticket = ticket
            activity.activity_type = 'TICKET'
            activity.project = None
        elif data.get('project_id') and int(data['project_id']) != project.id:
            other_project = get_object_or_404(Project, id=data['project_id'])
            # Vérifier que l'utilisateur est aussi membre de l'autre projet
            if other_project.members.filter(id=user.id).exists():
                activity.project = other_project
        
        activity.save()
        
        # Get member color for the activity
        project_members = list(project.members.all())
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
            '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
        ]
        member_colors = {}
        for i, member in enumerate(project_members):
            member_colors[member.id] = colors[i % len(colors)]
        
        return JsonResponse({
            'success': True,
            'message': 'Activité créée avec succès',
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'start_date': activity.start_datetime.isoformat(),
                'end_date': activity.end_datetime.isoformat(),
                'startDate': activity.start_datetime.isoformat(),
                'endDate': activity.end_datetime.isoformat(),
                'type': activity.activity_type,
                'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
                'employee_id': activity.employee.id,
                'employee_color': member_colors.get(activity.employee.id, '#A08D80'),
                'charge': float(activity.charge) if activity.charge else 0,
                'status': 'inprogress'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def project_search_suggestions(request):
    """
    API endpoint for project search suggestions with partial matching
    Returns JSON response with project suggestions for autocomplete
    """
    query = request.GET.get('q', '').strip()
    
    # Permettre la recherche dès 1 caractère au lieu de 2
    if not query or len(query) < 1:
        return JsonResponse({'suggestions': []})
    
    user = request.user
    
    # Filter projects based on user role
    if user.appRole == 'ADMIN':
        projects = Project.objects.all()
    elif user.appRole == 'MANAGER':
        projects = Project.objects.filter(project_manager=user)
    else:
        projects = Project.objects.filter(members=user)
    
    # Search with partial matching
    project_results = projects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(project_manager__first_name__icontains=query) |
        Q(project_manager__last_name__icontains=query) |
        Q(status__icontains=query) |
        Q(priority__icontains=query)
    ).distinct()[:10]  # Limit to 10 suggestions
    
    suggestions = []
    for project in project_results:
        # Calculate relevance score for better ordering
        relevance = 0
        query_lower = query.lower()
        if query_lower in project.title.lower():
            relevance += 10
            # Bonus pour les correspondances au début du titre
            if project.title.lower().startswith(query_lower):
                relevance += 5
        if query_lower in project.description.lower():
            relevance += 5
        
        suggestions.append({
            'id': project.id,
            'title': project.title,
            'description': project.description[:80] + '...' if len(project.description) > 80 else project.description,
            'status': project.status,
            'priority': project.priority,
            'manager': f"{project.project_manager.first_name} {project.project_manager.last_name}",
            'relevance': relevance,
            'url': f'/projects/details/{project.id}/'
        })
    
    # Sort by relevance score
    suggestions.sort(key=lambda x: x['relevance'], reverse=True)
    
    return JsonResponse({'suggestions': suggestions})
