from django.shortcuts import render
from .models import Ressource

# Create your views here.
def ressources(request):
    ressources = Ressource.objects.all()
    return render(request, 'ressources/ressources.html', {'ressources': ressources})

def ressourcesDetails(request, pk):
    ressource = Ressource.objects.get(pk=pk)
    return render(request, 'ressources/ressourcesDetails.html', {'ressource': ressource})
