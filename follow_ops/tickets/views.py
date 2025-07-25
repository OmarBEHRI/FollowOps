from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Ticket, CommentTicket
from ressources.models import Ressource


def tickets(request):
    """Vue pour afficher la liste des tickets"""
    tickets = Ticket.objects.all()
    return render(request, 'tickets.html', {'tickets': tickets})


@login_required
def ticketDetails(request, ticket_id):
    """Vue pour afficher les détails d'un ticket et gérer les commentaires"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    user = request.user
    
    # Vérifier les permissions de l'utilisateur
    can_comment = _user_can_comment(user, ticket)
    
    # Traitement des commentaires POST
    if request.method == 'POST' and can_comment:
        return _handle_comment_creation(request, ticket, user)
    
    # Récupérer les commentaires du ticket
    comments = ticket.comment_ticket.all().order_by('created_at')
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'can_comment': can_comment
    }
    
    return render(request, 'ticketDetails.html', context)


def _user_can_comment(user, ticket):
    """Vérifier si l'utilisateur peut commenter le ticket"""
    return (
        user.appRole == 'ADMIN' or 
        user.appRole == 'MANAGER' or 
        ticket.assigned_to.filter(id=user.id).exists()
    )


def _handle_comment_creation(request, ticket, user):
    """Gérer la création d'un nouveau commentaire"""
    content = request.POST.get('content')
    
    if not content:
        return redirect('ticketDetails', ticket_id=ticket.id)
    
    comment = CommentTicket.objects.create(
        ticket=ticket,
        content=content,
        author=user
    )
    
    # Réponse AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'id': comment.id,
            'content': comment.content,
            'author_name': comment.author.get_full_name(),
            'created_at': comment.created_at.strftime('%d %b %Y à %H:%M'),
            'author_avatar': comment.author.username
        })
    
    # Redirection normale
    return redirect('ticketDetails', ticket_id=ticket.id)
