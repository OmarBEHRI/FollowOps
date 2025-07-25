import random
from datetime import datetime, timedelta
from django.utils import timezone
from tickets.models import Ticket, CommentTicket
from activities.models import Activity

def seed_tickets(users, projects):
    """
    Create initial tickets for the application.
    Returns a list of created tickets.
    """
    # Define ticket data templates
    ticket_templates = [
        {
            'title': 'Bug dans le formulaire de contact',
            'description': 'Les utilisateurs signalent que le formulaire de contact ne fonctionne pas correctement. Les messages ne sont pas envoyés.',
            'status': 'Ouvert'
        },
        {
            'title': 'Amélioration de la page d\'accueil',
            'description': 'Ajouter une section de témoignages clients sur la page d\'accueil pour améliorer la conversion.',
            'status': 'En cours'
        },
        {
            'title': 'Optimisation des performances',
            'description': 'Le temps de chargement des pages est trop long. Optimiser les requêtes SQL et le chargement des assets.',
            'status': 'En cours'
        },
        {
            'title': 'Mise à jour de la documentation',
            'description': 'La documentation utilisateur doit être mise à jour pour refléter les dernières fonctionnalités.',
            'status': 'Ouvert'
        },
        {
            'title': 'Correction du bug d\'affichage sur mobile',
            'description': 'Sur les appareils mobiles, le menu de navigation ne s\'affiche pas correctement.',
            'status': 'Ferm '
        },
        {
            'title': 'Ajout de nouvelles fonctionnalités de recherche',
            'description': 'Implémenter une recherche avancée avec filtres et suggestions.',
            'status': 'Ouvert'
        },
        {
            'title': 'Intégration avec l\'API de paiement',
            'description': 'Intégrer notre système avec la nouvelle API de paiement pour permettre les transactions en temps réel.',
            'status': 'En cours'
        },
        {
            'title': 'Mise à jour des dépendances',
            'description': 'Mettre à jour toutes les bibliothèques et dépendances vers les dernières versions stables.',
            'status': 'Ferm '
        }
    ]
    
    created_tickets = []
    
    # Create tickets for each project
    for project in projects:
        # Skip projects that haven't started yet
        if not project.start_date:
            continue
            
        # Get project members for assignment
        members = list(project.members.all())
        
        # Create 2-4 tickets per project
        num_tickets = random.randint(2, 4)
        for _ in range(num_tickets):
            # Select a random ticket template
            template = random.choice(ticket_templates)
            
            # Create the ticket
            ticket = Ticket.objects.create(
                title=template['title'],
                description=template['description'],
                status=template['status'],
                created_at=project.start_date + timedelta(days=random.randint(1, max(2, (timezone.now().date() - project.start_date).days)))
            )
            
            # Assign 1-3 members to the ticket
            num_assignees = random.randint(1, min(3, len(members)))
            assignees = random.sample(members, num_assignees)
            for assignee in assignees:
                ticket.assigned_to.add(assignee)
            
            created_tickets.append(ticket)
    
    return created_tickets

def seed_ticket_activities_comments(users, tickets):
    """
    Add activities and comments to tickets.
    """
    # Add comments to tickets
    comment_templates = [
        "J'ai commencé à travailler sur ce ticket.",
        "Besoin d'informations supplémentaires pour résoudre ce problème.",
        "Le bug a été identifié, je travaille sur une solution.",
        "Correction implémentée, en attente de validation.",
        "Problème plus complexe que prévu, besoin de plus de temps.",
        "Ticket résolu, prêt pour les tests.",
        "Tests effectués, tout fonctionne correctement.",
        "Déployé en production, ticket peut être fermé.",
        "Problème récurrent, nécessite une solution plus robuste.",
        "Documentation mise à jour suite à cette correction."
    ]
    
    for ticket in tickets:
        # Add 1-4 comments per ticket
        num_comments = random.randint(1, 4)
        for _ in range(num_comments):
            comment = CommentTicket.objects.create(
                ticket=ticket,
                content=random.choice(comment_templates),
                author=random.choice(users)
            )
            ticket.comments.add(comment)
        
        # Add activities for tickets
        # Get assigned users
        assignees = list(ticket.assigned_to.all())
        if not assignees:  # Skip if no assignees
            continue
            
        # Add 1-3 activities per ticket
        num_activities = random.randint(1, 3)
        for _ in range(num_activities):
            # Random date after ticket creation
            days_since_creation = (timezone.now().date() - ticket.created_at.date()).days
            if days_since_creation <= 0:
                days_since_creation = 1
                
            activity_date = ticket.created_at.date() + timedelta(days=random.randint(0, days_since_creation))
            
            # Make sure it's a weekday (0-4 is Monday to Friday)
            while activity_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                activity_date = activity_date + timedelta(days=1)
            
            # Random start time between 9:00 and 16:00
            start_hour = random.randint(9, 16)
            start_minute = random.choice([0, 15, 30, 45])
            
            # Random duration between 30 minutes and 2 hours
            duration_hours = random.uniform(0.5, 2)
            
            # Create activity datetime objects
            start_datetime = datetime.combine(activity_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            
            # Create activity
            activity_titles = [
                "Analyse du problème",
                "Développement de la solution",
                "Test de la correction",
                "Revue de code",
                "Documentation",
                "Déploiement"
            ]
            
            Activity.objects.create(
                title=random.choice(activity_titles),
                description=f"Travail sur le ticket: {ticket.title}",
                employee=random.choice(assignees),
                activity_type="TICKET",
                ticket=ticket,
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )