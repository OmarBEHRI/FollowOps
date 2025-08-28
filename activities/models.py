from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
from django.utils import timezone
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
        
        # Recalculate availability rate for the employee after saving activity
        if self.employee:
            self._update_employee_availability_rate()
    
    def _update_employee_availability_rate(self):
        """
        Update the employee's availability rate based on their activities.
        """
        from datetime import timedelta
        from django.utils import timezone
        
        today = timezone.now().date()
        end_date = today + timedelta(days=30)  # Look ahead 30 days
        
        # Calculate total working hours for the period (8 hours per working day)
        working_days = 0
        current_date = today
        while current_date < end_date:
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                working_days += 1
            current_date += timedelta(days=1)
        
        total_working_hours = working_days * 8  # 8 hours per working day
        
        # Get activities for the employee in the future period
        future_activities = Activity.objects.filter(
            employee=self.employee,
            start_datetime__date__gte=today,
            start_datetime__date__lt=end_date
        )
        
        # Calculate allocated hours from activities
        allocated_hours = 0
        for activity in future_activities:
            duration = activity.end_datetime - activity.start_datetime
            allocated_hours += duration.total_seconds() / 3600
        
        # Calculate availability percentage
        if total_working_hours > 0:
            available_hours = max(0, total_working_hours - allocated_hours)
            availability_percentage = (available_hours / total_working_hours) * 100
        else:
            availability_percentage = 100
        
        # Update employee's availability rate
        availability_rate = min(100, max(0, round(availability_percentage)))
        if self.employee.availability_rate != availability_rate:
            self.employee.availability_rate = availability_rate
            self.employee.save(update_fields=['availability_rate'])
    
    def delete(self, *args, **kwargs):
        # Store employee reference before deletion
        employee = self.employee
        
        # Delete the activity
        super().delete(*args, **kwargs)
        
        # Recalculate availability rate for the employee after deletion
        if employee:
            self._update_employee_availability_rate_for_employee(employee)
    
    def _update_employee_availability_rate_for_employee(self, employee):
        """
        Update the given employee's availability rate based on their activities.
        Used when deleting activities.
        """
        from datetime import timedelta
        from django.utils import timezone
        
        today = timezone.now().date()
        end_date = today + timedelta(days=30)  # Look ahead 30 days
        
        # Calculate total working hours for the period (8 hours per working day)
        working_days = 0
        current_date = today
        while current_date < end_date:
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                working_days += 1
            current_date += timedelta(days=1)
        
        total_working_hours = working_days * 8  # 8 hours per working day
        
        # Get activities for the employee in the future period
        future_activities = Activity.objects.filter(
            employee=employee,
            start_datetime__date__gte=today,
            start_datetime__date__lt=end_date
        )
        
        # Calculate allocated hours from activities
        allocated_hours = 0
        for activity in future_activities:
            duration = activity.end_datetime - activity.start_datetime
            allocated_hours += duration.total_seconds() / 3600
        
        # Calculate availability percentage
        if total_working_hours > 0:
            available_hours = max(0, total_working_hours - allocated_hours)
            availability_percentage = (available_hours / total_working_hours) * 100
        else:
            availability_percentage = 100
        
        # Update employee's availability rate
        availability_rate = min(100, max(0, round(availability_percentage)))
        if employee.availability_rate != availability_rate:
            employee.availability_rate = availability_rate
            employee.save(update_fields=['availability_rate'])
    
    def __str__(self):
        return f"{self.title} - {self.employee} ({self.get_activity_type_display()})"


class UserActivityLog(models.Model):
    """
    Model to track user activity data for availability calculations.
    Stores both future scheduled activities (next 30 days) and historical data (past 3 months).
    """
    LOG_TYPES = [
        ('SCHEDULED', 'Scheduled Activity'),
        ('COMPLETED', 'Completed Activity'),
        ('CANCELLED', 'Cancelled Activity'),
    ]
    
    ALLOCATION_STATUS = [
        ('ALLOCATED', 'Allocated Time'),
        ('AVAILABLE', 'Available Time'),
    ]
    
    employee = models.ForeignKey(Ressource, on_delete=models.CASCADE, related_name='activity_logs')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    
    # Time tracking
    date = models.DateField()
    start_hour = models.IntegerField()  # 0-23 hour format
    end_hour = models.IntegerField()    # 0-23 hour format
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Status and type
    log_type = models.CharField(max_length=10, choices=LOG_TYPES)
    allocation_status = models.CharField(max_length=10, choices=ALLOCATION_STATUS)
    
    # Metadata for reporting
    project_id = models.IntegerField(null=True, blank=True)
    ticket_id = models.IntegerField(null=True, blank=True)
    activity_title = models.CharField(max_length=200, blank=True)
    
    # Efficiency tracking
    planned_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    efficiency_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'allocation_status']),
            models.Index(fields=['employee', 'log_type']),
        ]
        ordering = ['-date', 'start_hour']
    
    def save(self, *args, **kwargs):
        # Calculate efficiency ratio if both planned and actual hours are available
        if self.planned_hours and self.actual_hours and self.planned_hours > 0:
            self.efficiency_ratio = self.actual_hours / self.planned_hours
        
        # Calculate duration if not provided
        if not self.duration_hours and self.start_hour is not None and self.end_hour is not None:
            self.duration_hours = self.end_hour - self.start_hour
        
        super().save(*args, **kwargs)
    
    @classmethod
    def cleanup_old_logs(cls):
        """
        Remove logs older than 3 months to maintain performance.
        """
        cutoff_date = timezone.now().date() - timedelta(days=90)
        cls.objects.filter(date__lt=cutoff_date).delete()
    
    @classmethod
    def generate_future_availability_logs(cls, employee, days=30):
        """
        Generate availability logs for future dates based on working hours.
        Assumes 8-hour working days (8 AM to 6 PM) with 1-hour lunch break.
        """
        today = timezone.now().date()
        working_hours = [8, 9, 10, 11, 13, 14, 15, 16, 17]  # Skip 12 PM for lunch
        
        for i in range(days):
            future_date = today + timedelta(days=i+1)
            
            # Skip weekends
            if future_date.weekday() >= 5:
                continue
            
            # Check if there are existing logs for this date
            existing_logs = cls.objects.filter(employee=employee, date=future_date)
            allocated_hours = set(existing_logs.values_list('start_hour', flat=True))
            
            # Create availability logs for non-allocated hours
            for hour in working_hours:
                if hour not in allocated_hours:
                    cls.objects.get_or_create(
                        employee=employee,
                        date=future_date,
                        start_hour=hour,
                        defaults={
                            'end_hour': hour + 1,
                            'duration_hours': 1.0,
                            'log_type': 'SCHEDULED',
                            'allocation_status': 'AVAILABLE',
                            'activity_title': 'Available Time'
                        }
                    )
    
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.start_hour}:00-{self.end_hour}:00) - {self.get_allocation_status_display()}"