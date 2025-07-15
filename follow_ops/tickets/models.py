from django.db import models
from projects.models import Project
from ressources.models import Ressource

class Ticket(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(Ressource,  on_delete=models.SET_NULL, null=True, blank=True, related_name="assignedTickets")
    status = models.CharField(max_length=20, choices=[('Ouvert', 'Ouvert'), ('En cours', 'En cours'), ('Ferm ', 'Ferm ')])
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.ManyToManyField('Comment', related_name="ticket_comments", verbose_name="Commentaires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comment_ticket")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content}"