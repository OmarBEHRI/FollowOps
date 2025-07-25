from django.contrib.auth.models import AbstractUser
from django.db import models

class Ressource(AbstractUser):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    skills = models.TextField(blank=True)
    availability_rate = models.IntegerField(null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=200, choices=[
        ('Stagiaire', 'Stagiaire'),
        ('CDI', 'CDI'),
        ('Prestataire', 'Prestataire'),
        ('Alternant', 'Alternant'),
        ('CDD', 'CDD'),
        ('Autre', 'Autre')
    ])
    appRole = models.CharField(max_length=200, choices=[
        ('ADMIN', 'ADMIN'),
        ('MANAGER', 'MANAGER'),
        ('USER', 'USER')
    ])
    phone_number = models.CharField(max_length=20)
    entry_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(unique=True)
    # Supprimé: password = models.CharField(max_length=200)  # ❌ Ne pas redéfinir
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    completed_tickets_count = models.IntegerField(default=0)
    completed_projects_count = models.IntegerField(default=0)
    
    # Configuration pour utiliser l'email comme identifiant
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def get_assigned_tickets(self):
        # Retourne les tickets assignés à cette ressource
        return self.ticket_set.all()  # Ajustez selon votre modèle
    
    def get_hr_events(self):
        # Retourne les événements RH pour cette ressource
        return self.hrevent_set.all()  # Ajustez selon votre modèle
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
