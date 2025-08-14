from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, time
from ressources.models import Ressource
from projects.models import Project
from tickets.models import Ticket

# Supprimer ou assouplir les validations restrictives
def validate_working_hours(value):
    """Validate that the time is within working hours (8:00 - 18:00) - assoupli"""
    working_start = time(8, 0)
    working_end = time(18, 0)
    
    if value.time() < working_start or value.time() > working_end:
        raise ValidationError('Time must be within working hours (8:00 - 18:00)')

# Supprimer complètement la validation des jours ouvrables
# def validate_working_day(value):
#     """Validate that the date is a working day (Monday to Friday)"""
#     if value.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
#         raise ValidationError('Date must be a working day (Monday to Friday)')

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('PROJECT', 'Project'),
        ('TICKET', 'Ticket'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    employee = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES)
    
    # Optional relations - only one should be filled based on activity_type
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    
    # Assouplir les validations - supprimer validate_working_day
    start_datetime = models.DateTimeField(validators=[validate_working_hours])
    end_datetime = models.DateTimeField(validators=[validate_working_hours])
    
    # Calculated field for working hours
    charge = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        # Assouplir les validations - rendre projet/ticket optionnels
        # if self.activity_type == 'PROJECT' and not self.project:
        #     raise ValidationError({'project': 'Project must be set for PROJECT activity type'})
        # elif self.activity_type == 'TICKET' and not self.ticket:
        #     raise ValidationError({'ticket': 'Ticket must be set for TICKET activity type'})
            
        # Ensure start_datetime is before end_datetime
        if self.start_datetime and self.end_datetime and self.start_datetime >= self.end_datetime:
            raise ValidationError({'end_datetime': 'End time must be after start time'})
            
        # Allow multi-day activities but limit to 7 days maximum
        if self.start_datetime and self.end_datetime:
            duration_days = (self.end_datetime.date() - self.start_datetime.date()).days
            if duration_days > 7:
                raise ValidationError('Activity cannot span more than 7 days')
    
    def save(self, *args, **kwargs):
        # Calculate charge (working hours) before saving
        if self.start_datetime and self.end_datetime:
            # Calculate duration in hours
            duration = self.end_datetime - self.start_datetime
            hours = duration.total_seconds() / 3600
            self.charge = round(hours, 2)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.employee} ({self.get_activity_type_display()})"