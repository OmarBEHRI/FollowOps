from django.db import models
from django.utils import timezone
from ressources.models import Ressource

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('Basse', 'Basse'),
        ('Moyenne', 'Moyenne'),
        ('Haute', 'Haute'),
        ('Critique', 'Critique')
    ]
    
    STATUS_CHOICES = [
        ('Ouvert', 'Ouvert'),
        ('En cours', 'En cours'),
        ('Résolu', 'Résolu'),
        ('Fermé', 'Fermé')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ManyToManyField(Ressource, related_name="assignedTickets", blank=True)
    created_by = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name="createdTickets")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ouvert')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Moyenne')
    # Real dates - automatically set based on status
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de début réelle")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin réelle")
    comments = models.ManyToManyField('CommentTicket', related_name="ticket_comments", verbose_name="Commentaires", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Get the old status if this is an update
        old_status = None
        is_new = self.pk is None
        
        if self.pk:
            try:
                old_instance = Ticket.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Ticket.DoesNotExist:
                pass
        
        # Set real start date when status changes to 'En cours'
        if old_status != 'En cours' and self.status == 'En cours' and not self.start_date:
            self.start_date = timezone.now()
        
        # Set real end date when status changes to 'Résolu' or 'Fermé'
        if old_status not in ['Résolu', 'Fermé'] and self.status in ['Résolu', 'Fermé'] and not self.end_date:
            self.end_date = timezone.now()
        
        # Reset end date if status changes back from closed/resolved
        if old_status in ['Résolu', 'Fermé'] and self.status not in ['Résolu', 'Fermé']:
            self.end_date = None
        
        super().save(*args, **kwargs)
        
        # Create status log entry for new tickets or status changes
        if is_new or (old_status and old_status != self.status):
            TicketStatusLog.objects.create(
                ticket=self,
                status=self.status,
                changed_by=getattr(self, '_changed_by', None)
            )

    def __str__(self):
        return f"{self.title}"


class TicketStatusLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="status_logs")
    status = models.CharField(max_length=20, choices=Ticket.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(Ressource, on_delete=models.SET_NULL, null=True, related_name='ticket_status_changes')
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Ticket Status Log"
        verbose_name_plural = "Ticket Status Logs"
    
    def __str__(self):
        return f"Ticket {self.ticket.id} - {self.status} at {self.timestamp}"


class CommentTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comment_ticket")
    content = models.TextField()
    author = models.ForeignKey(Ressource, on_delete=models.SET_NULL, null=True, related_name='ticket_comments_authored')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content}..."