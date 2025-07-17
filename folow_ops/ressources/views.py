from django.shortcuts import render
from .models import Ressource

# Create your views here.
def ressources(request):
    ressources = Ressource.objects.all()
    return render(request, 'ressources.html', {'ressources': ressources})

from django.shortcuts import render, get_object_or_404
from .models import Ressource

# ... (autres imports et code existant)

def ressourcesDetails(request, id):
    ressource = get_object_or_404(Ressource, pk=id)
    return render(request, 'ressourcesDetails.html', {'ressource': ressource})

from django.shortcuts import redirect
from django.contrib import messages

def ressourcesDelete(request, id):
    ressource = get_object_or_404(Ressource, pk=id)
    ressource.delete()
    messages.success(request, 'La ressource a été supprimée avec succès.')
    return redirect('ressources')
