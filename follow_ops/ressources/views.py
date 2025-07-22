from django.shortcuts import render, redirect
from .models import Ressource

# Create your views here.
def ressources(request):
    ressources = Ressource.objects.all()
    return render(request, 'ressources.html', {'ressources': ressources})

def ressourcesDetails(request):
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
        
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            return render(request, 'add_resource.html', {'error': 'Les mots de passe ne correspondent pas'})
            
        username = email
        
        # Créer l'utilisateur avec le mot de passe hashé
        user = Ressource.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            status=status,
            phone_number=phone_number,
            entry_date=entry_date,
            location=location,
            availability_rate=availability_rate,
            skills=skills
        )
        return redirect('/ressources/')
    return render(request, 'add_resource.html')
