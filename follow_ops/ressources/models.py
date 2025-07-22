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
    password = models.CharField(max_length=200)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'role', 'status']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
