from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Project, Tag
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
    return render(request, 'projectInfo.html', {'project': project, 'pk': pk, 'active_tab': 'info'})


@login_required
def projectMembers(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projectMembers.html', {'project': project, 'pk': pk, 'active_tab': 'membres'})

@login_required
def projectCalendar(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projectCalendar.html', {'project': project, 'pk': pk, 'active_tab': 'calendrier'})


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
