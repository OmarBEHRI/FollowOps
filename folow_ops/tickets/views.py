from django.shortcuts import render

def tickets(request):
    return render(request, 'tickets.html')
