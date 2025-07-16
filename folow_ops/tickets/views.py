from django.shortcuts import render
from .models import Ticket

# Create your views here.
def tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'tickets/tickets.html', {'tickets': tickets})

def ticketDetails(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    return render(request, 'tickets/ticketDetails.html', {'ticket': ticket})
