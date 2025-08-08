from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Ticket, CommentTicket
from ressources.models import Ressource
from projects.models import Project
from django.contrib import messages
import json

# Variable temporaire pour tester sans authentification
TEST_MODE = True


@login_required
def tickets(request):
    """Vue pour afficher la liste des tickets selon le rôle de l'utilisateur"""
    user = request.user
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    # Base query with search filter if provided
    base_query = Ticket.objects.all()
    if search_query:
        base_query = base_query.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply status filter if provided
    if status_filter:
        base_query = base_query.filter(status=status_filter)
        
    # Apply priority filter if provided
    if priority_filter:
        base_query = base_query.filter(priority=priority_filter)
    
    # Filter tickets based on user role
    if user.appRole == 'ADMIN':
        # Admins can see all tickets
        tickets_list = base_query
    elif user.appRole == 'MANAGER':
        # Managers can see tickets they created
        tickets_list = base_query.filter(created_by=user)
    else:  # USER role
        # Regular users can see tickets assigned to them
        tickets_list = base_query.filter(assigned_to=user)
    
    context = {
        'tickets': tickets_list,
        'user_role': user.appRole,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES
    }
    
    return render(request, 'tickets.html', context)


def ticketDetails(request, ticket_id):
    """Vue pour afficher les détails d'un ticket et gérer les commentaires"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # En mode test, on utilise un utilisateur admin par défaut
    if TEST_MODE and not request.user.is_authenticated:
        user = Ressource.objects.filter(appRole='ADMIN').first()
        if not user:
            # Fallback si aucun admin n'est trouvé
            user = Ressource.objects.first()
    else:
        # Vérification de l'authentification en mode normal
        if not TEST_MODE and not request.user.is_authenticated:
            return redirect('login')
        user = request.user
    
    # Vérifier les permissions de l'utilisateur
    can_comment = True  # Tous les utilisateurs peuvent commenter
    can_edit = user.appRole in ['ADMIN', 'MANAGER'] and (user.appRole == 'ADMIN' or ticket.created_by == user)
    can_delete = user.appRole == 'ADMIN'
    
    # Traitement des commentaires POST
    if request.method == 'POST' and 'comment' in request.POST and can_comment:
        content = request.POST.get('comment')
        if content:
            comment = CommentTicket.objects.create(
                ticket=ticket,
                content=content,
                author=user
            )
            messages.success(request, 'Commentaire ajouté avec succès')
            return redirect('ticketDetails', ticket_id=ticket_id)
    
    # Récupérer les commentaires du ticket
    comments = ticket.comment_ticket.all().order_by('created_at')
    
    # Récupérer les ressources pour le formulaire d'assignation
    resources = Ressource.objects.all()
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'can_comment': can_comment,
        'can_edit': can_edit,
        'can_delete': can_delete,
        'resources': resources,
        'user_role': user.appRole
    }
    
    return render(request, 'ticketDetails.html', context)

@login_required
def create_ticket(request):
    """Vue pour créer un nouveau ticket"""
    user = request.user
    
    # Vérifier que l'utilisateur a les droits pour créer un ticket
    if user.appRole not in ['ADMIN', 'MANAGER']:
        messages.error(request, 'Vous n\'avez pas les droits pour créer un ticket')
        return redirect('tickets')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        assigned_to_ids = request.POST.getlist('assigned_to')
        
        if title and description:
            # Créer le ticket
            ticket = Ticket.objects.create(
                title=title,
                description=description,
                status=status or 'Ouvert',
                priority=priority or 'Moyenne',
                created_by=user
            )
            
            # Assigner les ressources
            if assigned_to_ids:
                resources = Ressource.objects.filter(id__in=assigned_to_ids)
                ticket.assigned_to.set(resources)
            
            messages.success(request, 'Ticket créé avec succès')
            return redirect('ticketDetails', ticket_id=ticket.id)
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires')
    
    # Récupérer les ressources pour le formulaire
    resources = Ressource.objects.all()
    
    context = {
        'resources': resources,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'user_role': user.appRole
    }
    
    return render(request, 'create_ticket.html', context)

@login_required
def edit_ticket(request, ticket_id):
    """Vue pour modifier un ticket existant"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    user = request.user
    
    # Vérifier que l'utilisateur a les droits pour modifier ce ticket
    if not (user.appRole == 'ADMIN' or (user.appRole == 'MANAGER' and ticket.created_by == user)):
        messages.error(request, 'Vous n\'avez pas les droits pour modifier ce ticket')
        return redirect('tickets')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        assigned_to_ids = request.POST.getlist('assigned_to')
        
        if title and description:
            # Mettre à jour le ticket
            ticket.title = title
            ticket.description = description
            ticket.status = status
            ticket.priority = priority
            ticket.save()
            
            # Mettre à jour les assignations
            if assigned_to_ids:
                resources = Ressource.objects.filter(id__in=assigned_to_ids)
                ticket.assigned_to.set(resources)
            else:
                ticket.assigned_to.clear()
            
            messages.success(request, 'Ticket mis à jour avec succès')
            return redirect('ticketDetails', ticket_id=ticket.id)
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires')
    
    # Récupérer les ressources pour le formulaire
    resources = Ressource.objects.all()
    assigned_resources = ticket.assigned_to.all()
    
    context = {
        'ticket': ticket,
        'resources': resources,
        'assigned_resources': assigned_resources,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'user_role': user.appRole
    }
    
    return render(request, 'edit_ticket.html', context)

@login_required
def delete_ticket(request, ticket_id):
    """Vue pour supprimer un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    user = request.user
    
    # Vérifier que l'utilisateur a les droits pour supprimer ce ticket
    if user.appRole != 'ADMIN':
        messages.error(request, 'Vous n\'avez pas les droits pour supprimer ce ticket')
        return redirect('tickets')
    
    if request.method == 'POST':
        ticket.delete()
        messages.success(request, 'Ticket supprimé avec succès')
        return redirect('tickets')
    
    return render(request, 'delete_ticket.html', {'ticket': ticket})


def add_comment_ajax(request, ticket_id):
    """Vue pour ajouter un commentaire via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # En mode test, on utilise un utilisateur admin par défaut
        if TEST_MODE and not request.user.is_authenticated:
            user = Ressource.objects.filter(appRole='ADMIN').first()
            if not user:
                # Fallback si aucun admin n'est trouvé
                user = Ressource.objects.first()
        else:
            # Vérification de l'authentification en mode normal
            if not TEST_MODE and not request.user.is_authenticated:
                return JsonResponse({'status': 'error', 'message': 'Authentification requise'}, status=401)
            user = request.user
        
        # Récupérer le ticket
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ticket non trouvé'}, status=404)
        
        # Récupérer le contenu du commentaire
        data = json.loads(request.body)
        content = data.get('comment', '')
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Le commentaire ne peut pas être vide'}, status=400)
        
        # Créer le commentaire
        comment = CommentTicket.objects.create(
            ticket=ticket,
            content=content,
            author=user
        )
        
        # Préparer les données pour la réponse
        # Utiliser une valeur par défaut pour gender car Ressource n'a pas cet attribut
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'author_name': comment.author.get_full_name(),
            'author_gender': getattr(comment.author, 'gender', 'M'),  # Valeur par défaut 'M' si l'attribut n'existe pas
            'author_id': comment.author.id,
            'author_role': getattr(comment.author, 'role', 'Membre'),  # Inclure le rôle de l'auteur
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),  # Format de date mis à jour pour correspondre à l'UI
        }
        
        return JsonResponse({
            'status': 'success',
            'comment': comment_data
        })
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)


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


@login_required
def get_resources_list(request):
    """Récupérer la liste des projets et tickets pour le formulaire d'activité"""
    resource_type = request.GET.get('type')
    user = request.user
    
    if resource_type == 'project':
        # Filtrer les projets où l'utilisateur est membre
        projects = Project.objects.filter(members=user).values('id', 'title')
        return JsonResponse({
            'success': True,
            'resources': list(projects)
        })
    elif resource_type == 'ticket':
        # Filtrer les tickets assignés à l'utilisateur
        tickets = Ticket.objects.filter(assigned_to=user).values('id', 'title')
        return JsonResponse({
            'success': True,
            'resources': list(tickets)
        })
    
    return JsonResponse({'success': False, 'error': 'Type de ressource invalide'})


@login_required
def get_user_tickets_api(request):
    """API endpoint pour récupérer les tickets de l'utilisateur connecté"""
    user = request.user
    
    # Filtrer les tickets selon le rôle de l'utilisateur
    if user.appRole == 'ADMIN':
        # Admin voit tous les tickets
        tickets = Ticket.objects.all()
    elif user.appRole == 'MANAGER':
        # Manager voit les tickets qu'il a créés
        tickets = Ticket.objects.filter(created_by=user)
    else:
        # Utilisateur normal voit les tickets qui lui sont assignés
        tickets = Ticket.objects.filter(assigned_to=user)
    
    tickets_data = [{
        'id': ticket.id,
        'title': ticket.title
    } for ticket in tickets]
    
    return JsonResponse(tickets_data, safe=False)
