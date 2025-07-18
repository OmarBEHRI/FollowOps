from django.shortcuts import render
from .models import Ticket

# Create your views here.
def tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets.html', {'tickets': tickets})

def ticketDetails(request):
    return render(request, 'ticketDetails.html')
