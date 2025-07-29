from django.db import models
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
    comments = models.ManyToManyField('CommentTicket', related_name="ticket_comments", verbose_name="Commentaires", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class CommentTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comment_ticket")
    content = models.TextField()
    author = models.ForeignKey(Ressource, on_delete=models.SET_NULL, null=True, related_name='ticket_comments_authored')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content}..."