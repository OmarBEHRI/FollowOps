from django.db import models
from django.utils import timezone
from ressources.models import Ressource

class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="Intitulé")
    description = models.TextField(verbose_name="Description détailée")
    type = models.CharField(max_length=20, choices=[
        ('BUILD', 'Projet (BUILD)'),
        ('RUN', 'RUN'),
    ], verbose_name="Type de projet")
    status = models.CharField(max_length=20, choices=[
        ('À initier', 'À initier'),
        ('En cours', 'En cours'),
        ('Terminé', 'Terminé'),
        ('Suspendu', 'Suspendu'),
        ('Annulé', 'Annulé'),
    ], verbose_name="Statut")
    priority = models.CharField(max_length=20, choices=[
        ('Basse', 'Basse'),
        ('Moyenne', 'Moyenne'),
        ('Haute', 'Haute'),
        ('Critique', 'Critique'),
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
    comments = models.ManyToManyField('CommentProject', related_name="project_comments", verbose_name="Commentaires", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Get the old status if this is an update
        old_status = None
        if self.pk:
            try:
                old_instance = Project.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Project.DoesNotExist:
                pass
        
        # Set real start date when status changes to 'En cours'
        if old_status != 'En cours' and self.status == 'En cours' and not self.start_date:
            self.start_date = timezone.now().date()
        
        # Set real end date when status changes to 'Terminé'
        if old_status != 'Terminé' and self.status == 'Terminé' and not self.end_date:
            self.end_date = timezone.now().date()
        
        # Reset end date if status changes back from finished
        if old_status == 'Terminé' and self.status != 'Terminé':
            self.end_date = None
        
        # Reset start date if status changes back to 'À initier'
        if self.status == 'À initier':
            self.start_date = None
            self.end_date = None
        
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tag")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CommentProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="comment_project")
    content = models.TextField(verbose_name="Contenu")
    author = models.ForeignKey('ressources.Ressource', on_delete=models.SET_NULL, null=True, related_name='project_comments_authored')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content}"



