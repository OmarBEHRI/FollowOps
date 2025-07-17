from django.shortcuts import render
from .models import Ressource

# Create your views here.
def ressources(request):
    ressources = Ressource.objects.all()
    return render(request, 'ressources.html', {'ressources': ressources})

def ressourcesDetails(request):
    return render(request, 'ressourcesDetails.html')
