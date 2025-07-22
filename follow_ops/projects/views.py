from django.shortcuts import render
from .models import Project

def projects(request):
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects})


def projectDetails(request, pk):
    # Données statiques pour l'affichage
    project = {
        'title': "Projet de développement d'application mobile",
        'description': "Création d'une application mobile pour la gestion de tickets et de projets.",
        'type': "Application mobile",
        'status': "En cours",
        'priority': "Haute",
        'project_manager': "Sophie Martin",
        'expected_start_date': "01/01/2024",
        'expected_end_date': "31/12/2024",
        'start_date': "01/01/2024",
        'end_date': "En cours",
        'estimated_charges': 120,
        'progress': [20, 35, 50, 65, 70, 80, 90],
        'tags': ["Mobile", "Gestion de projet", "Productivité"]
    }
    return render(request, 'projectsDetails.html', {'project': project, 'pk': pk})

