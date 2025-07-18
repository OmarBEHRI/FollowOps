from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Intitulé")
    description = models.TextField(verbose_name="Description détailée")
    type = models.CharField(max_length=20, choices=[
        ('BUILD', 'Projet (BUILD)'),
        ('RUN', 'RUN'),
    ], verbose_name="Type de projet")
    status = models.CharField(max_length=20, choices=[
        ('À initier', 'To init'),
        ('En cours', 'In progress'),
        ('Terminé', 'Finished'),
        ('Suspendu', 'Suspended'),
        ('Annulé', 'Cancelled'),
    ], verbose_name="Statut")
    priority = models.CharField(max_length=20, choices=[
        ('Basse', 'Low'),
        ('Moyenne', 'Medium'),
        ('Haute', 'High'),
        ('Critique', 'Critical'),
    ], verbose_name="Priorité")
    project_manager = models.ForeignKey('ressources.Ressource', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_manager', verbose_name="Chef de projet")
    expected_start_date = models.DateField(verbose_name="Date de début prévue")
    expected_end_date = models.DateField(verbose_name="Date de fin prévue")
    start_date = models.DateField(null=True, blank=True, verbose_name="Date de début réelle")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin réelle")
    members = models.ManyToManyField('ressources.Ressource', related_name='members', verbose_name="Membres du projet")
    estimated_charges = models.IntegerField(verbose_name="Charges estimées (en jours ou heures)")
    progress = models.IntegerField(verbose_name="Avancement (%)")
    tags = models.ManyToManyField('Tag', related_name='projects', verbose_name="Tags ou categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tag")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



