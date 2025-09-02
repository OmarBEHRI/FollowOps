import random
from datetime import datetime, timedelta
from django.utils import timezone
from tickets.models import Ticket, TicketStatusLog
from projects.models import Project, ProjectStatusLog
from ressources.models import Ressource

def seed_ticket_status_logs(tickets, users):
    """
    Create historical status logs for tickets to simulate realistic status changes over time.
    """
    created_logs = []
    
    for ticket in tickets:
        # Get the ticket creation date
        creation_date = ticket.created_at
        current_date = creation_date
        current_status = 'Ouvert'  # All tickets start as 'Ouvert'
        
        # Create initial status log for ticket creation
        log = TicketStatusLog.objects.create(
            ticket=ticket,
            status=current_status,
            timestamp=creation_date,
            changed_by=ticket.created_by
        )
        created_logs.append(log)
        
        # Define possible status transitions
        status_transitions = {
            'Ouvert': ['En cours', 'Fermé'],
            'En cours': ['Résolu', 'Ouvert', 'Fermé'],
            'Résolu': ['Fermé', 'En cours'],
            'Fermé': []  # Final status
        }
        
        # Simulate status changes over time until we reach the current status
        max_days = max(1, (timezone.now() - creation_date).days)  # Ensure at least 1 day
        
        # Create more status changes for better visualization
        num_changes = random.randint(1, min(6, max(1, max_days)))  # 1-6 status changes per ticket, but not more than max_days
        if max_days > 1:
            change_intervals = sorted([random.randint(1, max_days) for _ in range(num_changes)])
        else:
            change_intervals = [1]  # Single change if only 1 day available
        
        for i, days_to_change in enumerate(change_intervals):
            if days_to_change >= max_days:
                break
                
            possible_next_statuses = status_transitions.get(current_status, [])
            
            if possible_next_statuses:
                # For the last change, bias towards final status
                if i == len(change_intervals) - 1 and ticket.status in possible_next_statuses:
                    next_status = ticket.status
                elif ticket.status in possible_next_statuses and random.random() < 0.4:
                    next_status = ticket.status
                else:
                    next_status = random.choice(possible_next_statuses)
                
                # Create status change log
                change_date = creation_date + timedelta(days=days_to_change)
                
                # Don't create logs in the future
                if change_date > timezone.now():
                    break
                
                log = TicketStatusLog.objects.create(
                    ticket=ticket,
                    status=next_status,
                    timestamp=change_date,
                    changed_by=random.choice(users)
                )
                created_logs.append(log)
                current_status = next_status
        
        # If we haven't reached the final status, create one more log
        if current_status != ticket.status:
            final_date = creation_date + timedelta(days=max_days + random.randint(1, 3))
            if final_date <= timezone.now():
                log = TicketStatusLog.objects.create(
                    ticket=ticket,
                    status=ticket.status,
                    timestamp=final_date,
                    changed_by=random.choice(users)
                )
                created_logs.append(log)
    
    return created_logs

def seed_project_status_logs(projects, users):
    """
    Create historical status logs for projects to simulate realistic status changes over time.
    """
    created_logs = []
    
    for project in projects:
        # Get the project creation date
        creation_date = project.created_at
        current_date = creation_date
        current_status = 'À initier'  # All projects start as 'À initier'
        
        # Create initial status log for project creation
        log = ProjectStatusLog.objects.create(
            project=project,
            status=current_status,
            timestamp=creation_date,
            changed_by=project.project_manager or random.choice(users)
        )
        created_logs.append(log)
        
        # Define possible status transitions
        status_transitions = {
            'À initier': ['En cours', 'Suspendu', 'Annulé'],
            'En cours': ['Terminé', 'Suspendu', 'À initier'],
            'Terminé': [],  # Final status
            'Suspendu': ['En cours', 'Annulé', 'À initier'],
            'Annulé': []  # Final status
        }
        
        # Simulate 2-6 status changes over the full time span available
        max_days = max(1, (timezone.now() - creation_date).days)  # Ensure at least 1 day
        num_changes = random.randint(1, min(6, max(1, max_days)))  # 1-6 status changes, don't exceed available days
        
        for change_num in range(num_changes):
            possible_next_statuses = status_transitions.get(current_status, [])
            
            if not possible_next_statuses:
                break
                
            # Choose next status, with increasing bias towards the final project status
            bias_factor = 0.3 + (change_num / num_changes) * 0.5  # Increase bias over time
            if project.status in possible_next_statuses and random.random() < bias_factor:
                next_status = project.status
            else:
                next_status = random.choice(possible_next_statuses)
            
            # Create status change log at a random time within the available span
            # Distribute changes more evenly across the time span
            min_days = int((change_num / num_changes) * max_days)
            max_days_for_change = int(((change_num + 1) / num_changes) * max_days)
            
            if min_days <= max_days_for_change and max_days > 0:
                days_offset = random.randint(min_days, min(max_days_for_change, max_days)) if min_days < min(max_days_for_change, max_days) else min_days
                change_date = creation_date + timedelta(days=days_offset)
                
                # Don't create logs in the future
                if change_date > timezone.now():
                    break
                
                log = ProjectStatusLog.objects.create(
                    project=project,
                    status=next_status,
                    timestamp=change_date,
                    changed_by=project.project_manager or random.choice(users)
                )
                created_logs.append(log)
                current_status = next_status
                
                # If we've reached the final status, stop
                if current_status == project.status:
                    break
        
        # If we haven't reached the final status, create one more log
        if current_status != project.status:
            final_date = creation_date + timedelta(days=max_days + random.randint(1, 7))
            if final_date <= timezone.now():
                log = ProjectStatusLog.objects.create(
                    project=project,
                    status=project.status,
                    timestamp=final_date,
                    changed_by=project.project_manager or random.choice(users)
                )
                created_logs.append(log)
    
    return created_logs

def seed_status_logs(users, projects, tickets):
    """
    Main function to seed all status logs.
    """
    print("Seeding ticket status logs...")
    ticket_logs = seed_ticket_status_logs(tickets, users)
    
    print("Seeding project status logs...")
    project_logs = seed_project_status_logs(projects, users)
    
    return ticket_logs, project_logs