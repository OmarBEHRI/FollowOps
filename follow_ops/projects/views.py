from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Project, Tag, CommentProject
from .forms import ProjectForm
from ressources.models import Ressource

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
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'project_managers': project_managers,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_project_manager': project_manager_filter
    })


@login_required
def create_project(request):
    if request.user.appRole not in ['ADMIN', 'MANAGER']:
        return redirect('projects')
        
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
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
            
            return redirect('projects')
    else:
        form = ProjectForm()
    
    return render(request, 'project_form.html', {'form': form})

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
    
    # Format activities for the calendar
    calendar_activities = []
    for activity in activities:
        calendar_activities.append({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'start_date': activity.start_datetime.date(),
            'end_date': activity.end_datetime.date(),
            'employee': f"{activity.employee.first_name} {activity.employee.last_name}",
            'charge': activity.charge
        })
    
    # Get calendar information for the current month
    cal = calendar.monthcalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]
    
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
        'can_edit': can_edit
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
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    
    # Check if user has permission to edit the project
    if not (user.appRole == 'ADMIN' or (user.appRole == 'MANAGER' and project.project_manager == user)):
        return redirect('projectDetails', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            
            # Update members if provided
            members = form.cleaned_data.get('members')
            if members:
                project.members.set(members)
            
            return redirect('projectDetails', pk=pk)
    else:
        form = ProjectForm(instance=project)
        # Preselect current members
        form.fields['members'].initial = project.members.all()
    
    return render(request, 'project_form.html', {'form': form, 'edit_mode': True, 'project': project})


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
