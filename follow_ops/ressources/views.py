from django.shortcuts import render, redirect
from .models import Ressource
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
import pandas as pd
from urllib.parse import quote
from datetime import datetime

@login_required
def ressources(request):
    user = request.user
    ressources = Ressource.objects.all()

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


def ressourcesDetails(request, resource_id=None):
    if resource_id:
        resource = Ressource.objects.get(id=resource_id)
        return render(request, 'ressourcesDetails.html', {'resource': resource})
    return render(request, 'ressourcesDetails.html')


def add_resource(request):
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


def edit_resource(request, resource_id):
    resource = Ressource.objects.get(id=resource_id)
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
