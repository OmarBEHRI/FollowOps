from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from activities.models import UserActivityLog, Activity
from ressources.models import Ressource
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cleanup and optimize activity logs data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=90,
            help='Number of days to keep historical data (default: 90)',
        )
        parser.add_argument(
            '--sync-activities',
            action='store_true',
            help='Synchronize UserActivityLog with Activity model data',
        )
        parser.add_argument(
            '--generate-future-logs',
            action='store_true',
            help='Generate future availability logs for all active employees',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_back = options['days_back']
        sync_activities = options['sync_activities']
        generate_future_logs = options['generate_future_logs']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting activity logs cleanup (dry_run={dry_run})')
        )
        
        # 1. Cleanup old logs
        self.cleanup_old_logs(days_back, dry_run)
        
        # 2. Sync activities if requested
        if sync_activities:
            self.sync_activity_logs(dry_run)
        
        # 3. Generate future logs if requested
        if generate_future_logs:
            self.generate_future_availability_logs(dry_run)
        
        # 4. Optimize database
        self.optimize_database(dry_run)
        
        self.stdout.write(
            self.style.SUCCESS('Activity logs cleanup completed successfully')
        )
    
    def cleanup_old_logs(self, days_back, dry_run):
        """Remove logs older than specified days"""
        cutoff_date = timezone.now().date() - timedelta(days=days_back)
        
        old_logs = UserActivityLog.objects.filter(
            date__lt=cutoff_date,
            log_type__in=['COMPLETED', 'CANCELLED']
        )
        
        count = old_logs.count()
        
        if count > 0:
            self.stdout.write(
                f'Found {count} old logs to cleanup (older than {cutoff_date})'
            )
            
            if not dry_run:
                with transaction.atomic():
                    deleted_count, _ = old_logs.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'Deleted {deleted_count} old activity logs')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'DRY RUN: Would delete {count} old logs')
                )
        else:
            self.stdout.write('No old logs found to cleanup')
    
    def sync_activity_logs(self, dry_run):
        """Synchronize UserActivityLog with Activity model data"""
        self.stdout.write('Synchronizing activity logs with Activity model...')
        
        activities = Activity.objects.all()
        synced_count = 0
        created_count = 0
        
        for activity in activities:
            try:
                if not dry_run:
                    from activities.services import AvailabilityCalculationService
                    AvailabilityCalculationService.sync_activity_logs(activity.employee.id)
                    synced_count += 1
                else:
                    synced_count += 1
                    
            except Exception as e:
                logger.error(f'Error syncing activity {activity.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'Error syncing activity {activity.id}: {str(e)}')
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Synchronized logs for {synced_count} employees')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would sync logs for {synced_count} employees')
            )
    
    def generate_future_availability_logs(self, dry_run):
        """Generate future availability logs for all active employees"""
        self.stdout.write('Generating future availability logs...')
        
        active_employees = Ressource.objects.filter(status='active')
        generated_count = 0
        
        for employee in active_employees:
            try:
                if not dry_run:
                    UserActivityLog.generate_future_availability_logs(employee.id)
                    generated_count += 1
                else:
                    generated_count += 1
                    
            except Exception as e:
                logger.error(f'Error generating logs for employee {employee.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'Error generating logs for employee {employee.id}: {str(e)}')
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Generated future logs for {generated_count} employees')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would generate logs for {generated_count} employees')
            )
    
    def optimize_database(self, dry_run):
        """Optimize database performance"""
        self.stdout.write('Optimizing database...')
        
        if not dry_run:
            # Remove duplicate logs
            duplicates_query = """
                DELETE t1 FROM activities_useractivitylog t1
                INNER JOIN activities_useractivitylog t2 
                WHERE t1.id > t2.id 
                AND t1.employee_id = t2.employee_id 
                AND t1.date = t2.date 
                AND t1.start_hour = t2.start_hour 
                AND t1.end_hour = t2.end_hour
                AND t1.log_type = t2.log_type
            """
            
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(duplicates_query)
                    affected_rows = cursor.rowcount
                    
                if affected_rows > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'Removed {affected_rows} duplicate logs')
                    )
                else:
                    self.stdout.write('No duplicate logs found')
                    
            except Exception as e:
                logger.error(f'Error removing duplicates: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'Error removing duplicates: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('DRY RUN: Would optimize database and remove duplicates')
            )
        
        # Show statistics
        total_logs = UserActivityLog.objects.count()
        scheduled_logs = UserActivityLog.objects.filter(log_type='SCHEDULED').count()
        completed_logs = UserActivityLog.objects.filter(log_type='COMPLETED').count()
        cancelled_logs = UserActivityLog.objects.filter(log_type='CANCELLED').count()
        
        self.stdout.write('\n=== Activity Logs Statistics ===')
        self.stdout.write(f'Total logs: {total_logs}')
        self.stdout.write(f'Scheduled logs: {scheduled_logs}')
        self.stdout.write(f'Completed logs: {completed_logs}')
        self.stdout.write(f'Cancelled logs: {cancelled_logs}')
        self.stdout.write('================================\n')