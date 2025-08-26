from datetime import datetime, timedelta, time
from collections import defaultdict
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from .models import Activity, UserActivityLog
from ressources.models import Ressource
from collections import defaultdict
import json


class AvailabilityCalculationService:
    """
    Service class for calculating user availability and generating activity data.
    """
    
    WORKING_HOURS = [8, 9, 10, 11, 13, 14, 15, 16, 17]  # Skip 12 PM for lunch
    WORKING_HOURS_PER_DAY = len(WORKING_HOURS)
    WORKING_END_HOUR = 18  # 6 PM
    
    @classmethod
    def calculate_availability_percentage(cls, employee_id, days=30):
        """
        Calculate the average availability percentage for the next N days.
        
        Args:
            employee_id: ID of the employee
            days: Number of days to look ahead (default 30)
            
        Returns:
            dict: {
                'availability_percentage': float,
                'total_working_hours': int,
                'allocated_hours': int,
                'available_hours': int
            }
        """
        try:
            employee = Ressource.objects.get(id=employee_id)
        except Ressource.DoesNotExist:
            return {'error': 'Employee not found'}
        
        # Generate future availability logs if they don't exist
        cls._ensure_future_logs_exist(employee, days)
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        # Get all activities for the next N days
        future_activities = Activity.objects.filter(
            employee=employee,
            start_datetime__date__gte=today,
            start_datetime__date__lt=end_date
        )
        
        # Calculate working days (exclude weekends)
        working_days = 0
        current_date = today
        while current_date < end_date:
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                working_days += 1
            current_date += timedelta(days=1)
        
        total_working_hours = working_days * cls.WORKING_HOURS_PER_DAY
        
        # Calculate allocated hours from activities
        allocated_hours = 0
        for activity in future_activities:
            duration = activity.end_datetime - activity.start_datetime
            allocated_hours += duration.total_seconds() / 3600
        
        available_hours = max(0, total_working_hours - allocated_hours)
        availability_percentage = (available_hours / total_working_hours * 100) if total_working_hours > 0 else 0
        
        return {
            'availability_percentage': round(availability_percentage, 2),
            'total_working_hours': total_working_hours,
            'allocated_hours': round(allocated_hours, 2),
            'available_hours': round(available_hours, 2),
            'working_days': working_days
        }
    
    @classmethod
    def get_hourly_breakdown_data(cls, employee_id, days=30):
        """
        Get daily breakdown data for visualization with days on x-axis and hours on y-axis.
        
        Returns:
            dict: {
                'chart_data': list of daily data,
                'summary': summary statistics
            }
        """
        try:
            employee = Ressource.objects.get(id=employee_id)
        except Ressource.DoesNotExist:
            return {'error': 'Employee not found'}
        
        # Generate future availability logs if they don't exist
        cls._ensure_future_logs_exist(employee, days)
        
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        # Get all activities for the period
        activities = Activity.objects.filter(
            employee=employee,
            start_datetime__date__gte=today,
            start_datetime__date__lt=end_date
        ).order_by('start_datetime')
        
        # Initialize daily data structure
        daily_data = []
        
        # Process each day in the range
        current_date = today
        while current_date < end_date:
            day_activities = activities.filter(start_datetime__date=current_date)
            
            # Calculate hours for this day
            allocated_hours = 0
            available_hours = 0
            
            if current_date.weekday() < 5:  # Weekdays only
                # Start with 8 working hours available
                available_hours = 8
                
                # Calculate allocated hours from activities
                for activity in day_activities:
                    start_time = activity.start_datetime
                    end_time = activity.end_datetime
                    
                    # Calculate duration in hours
                    duration = (end_time - start_time).total_seconds() / 3600
                    allocated_hours += duration
                
                # Adjust available hours
                available_hours = max(0, available_hours - allocated_hours)
            
            daily_data.append({
                'date': current_date,
                'date_label': current_date.strftime('%m/%d'),
                'day_name': current_date.strftime('%a'),
                'allocated_hours': round(allocated_hours, 2),
                'available_hours': round(available_hours, 2),
                'total_hours': round(allocated_hours + available_hours, 2),
                'is_weekend': current_date.weekday() >= 5,
                'utilization_percentage': round((allocated_hours / (allocated_hours + available_hours) * 100), 2) if (allocated_hours + available_hours) > 0 else 0
            })
            
            current_date += timedelta(days=1)
        
        # Calculate summary statistics
        total_allocated = sum(d['allocated_hours'] for d in daily_data)
        total_available = sum(d['available_hours'] for d in daily_data)
        total_hours = total_allocated + total_available
        
        summary = {
            'total_allocated_hours': round(total_allocated, 2),
            'total_available_hours': round(total_available, 2),
            'total_hours': round(total_hours, 2),
            'overall_utilization': round((total_allocated / total_hours * 100), 2) if total_hours > 0 else 0,
            'average_daily_allocation': round(total_allocated / len([d for d in daily_data if not d['is_weekend']]), 2) if len([d for d in daily_data if not d['is_weekend']]) > 0 else 0
        }
        
        return {
            'chart_data': daily_data,
            'summary': summary
        }
    
    @classmethod
    def get_activity_trends_data(cls, employee_id, days_back=90):
        """
        Get historical activity trends for reporting.
        
        Args:
            employee_id: ID of the employee
            days_back: Number of days to look back (default 90)
            
        Returns:
            dict: Activity trends and efficiency metrics
        """
        try:
            employee = Ressource.objects.get(id=employee_id)
        except Ressource.DoesNotExist:
            return {'error': 'Employee not found'}
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        # Get activity logs for the period
        activity_logs = UserActivityLog.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Group by week for trend analysis
        weekly_data = defaultdict(lambda: {
            'allocated_hours': 0,
            'available_hours': 0,
            'efficiency_sum': 0,
            'efficiency_count': 0,
            'week_start': None
        })
        
        for log in activity_logs:
            # Get week start (Monday)
            week_start = log.date - timedelta(days=log.date.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if weekly_data[week_key]['week_start'] is None:
                weekly_data[week_key]['week_start'] = week_start
            
            if log.allocation_status == 'ALLOCATED':
                weekly_data[week_key]['allocated_hours'] += float(log.duration_hours)
            else:
                weekly_data[week_key]['available_hours'] += float(log.duration_hours)
            
            if log.efficiency_ratio:
                weekly_data[week_key]['efficiency_sum'] += float(log.efficiency_ratio)
                weekly_data[week_key]['efficiency_count'] += 1
        
        # Convert to list format
        trends = []
        for week_key, data in sorted(weekly_data.items()):
            avg_efficiency = (data['efficiency_sum'] / data['efficiency_count']) if data['efficiency_count'] > 0 else 0
            utilization = (data['allocated_hours'] / (data['allocated_hours'] + data['available_hours']) * 100) if (data['allocated_hours'] + data['available_hours']) > 0 else 0
            
            trends.append({
                'week_start': data['week_start'],
                'allocated_hours': data['allocated_hours'],
                'available_hours': data['available_hours'],
                'utilization_percentage': round(utilization, 2),
                'average_efficiency': round(avg_efficiency, 2)
            })
        
        return {
            'trends': trends,
            'period_start': start_date,
            'period_end': end_date,
            'total_weeks': len(trends)
        }
    
    @classmethod
    def _ensure_future_logs_exist(cls, employee, days=30):
        """
        Ensure that future availability logs exist for the employee.
        """
        UserActivityLog.generate_future_availability_logs(employee, days)
    
    @classmethod
    def get_comprehensive_activity_report(cls, employee_id, months_back=3, months_forward=1):
        """
        Get comprehensive activity report for the specified time period.
        
        Args:
            employee_id: ID of the employee
            months_back: Number of months to look back (default 3)
            months_forward: Number of months to look forward (default 1)
            
        Returns:
            dict: Comprehensive activity data including detailed activities, summaries, and trends
        """
        try:
            employee = Ressource.objects.get(id=employee_id)
        except Ressource.DoesNotExist:
            return {'error': 'Employee not found'}
        
        today = timezone.now().date()
        start_date = today - timedelta(days=months_back * 30)
        end_date = today + timedelta(days=months_forward * 30)
        
        # Get all activities in the period
        activities = Activity.objects.filter(
            employee=employee,
            start_datetime__date__gte=start_date,
            start_datetime__date__lte=end_date
        ).select_related('project', 'ticket').order_by('start_datetime')
        
        # Get activity logs for the period
        activity_logs = UserActivityLog.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', 'start_hour')
        
        # Process activities by month
        monthly_data = defaultdict(lambda: {
            'activities': [],
            'total_hours': 0,
            'allocated_hours': 0,
            'available_hours': 0,
            'project_hours': 0,
            'ticket_hours': 0,
            'efficiency_scores': [],
            'working_days': 0
        })
        
        # Process detailed activities
        detailed_activities = []
        for activity in activities:
            month_key = activity.start_datetime.strftime('%Y-%m')
            duration_hours = float(activity.charge)
            
            activity_detail = {
                'date': activity.start_datetime.date(),
                'title': activity.title,
                'description': activity.description,
                'type': activity.get_activity_type_display(),
                'start_time': activity.start_datetime.time(),
                'end_time': activity.end_datetime.time(),
                'duration_hours': duration_hours,
                'project_name': activity.project.title if activity.project else None,
                'ticket_name': activity.ticket.title if activity.ticket else None,
                'status': 'Completed' if activity.start_datetime.date() <= today else 'Scheduled'
            }
            
            detailed_activities.append(activity_detail)
            
            # Update monthly statistics
            monthly_data[month_key]['activities'].append(activity_detail)
            monthly_data[month_key]['allocated_hours'] += duration_hours
            
            if activity.activity_type == 'PROJECT':
                monthly_data[month_key]['project_hours'] += duration_hours
            else:
                monthly_data[month_key]['ticket_hours'] += duration_hours
        
        # Process activity logs for availability data
        for log in activity_logs:
            month_key = log.date.strftime('%Y-%m')
            duration = float(log.duration_hours)
            
            if log.allocation_status == 'AVAILABLE':
                monthly_data[month_key]['available_hours'] += duration
            
            if log.efficiency_ratio:
                monthly_data[month_key]['efficiency_scores'].append(float(log.efficiency_ratio))
        
        # Calculate working days for each month
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Weekdays only
                month_key = current_date.strftime('%Y-%m')
                monthly_data[month_key]['working_days'] += 1
            current_date += timedelta(days=1)
        
        # Calculate totals and averages for each month
        monthly_summary = []
        for month_key, data in sorted(monthly_data.items()):
            total_hours = data['allocated_hours'] + data['available_hours']
            avg_efficiency = sum(data['efficiency_scores']) / len(data['efficiency_scores']) if data['efficiency_scores'] else 0
            utilization = (data['allocated_hours'] / total_hours * 100) if total_hours > 0 else 0
            
            monthly_summary.append({
                'month': month_key,
                'month_name': datetime.strptime(month_key, '%Y-%m').strftime('%B %Y'),
                'working_days': data['working_days'],
                'total_hours': round(total_hours, 2),
                'allocated_hours': round(data['allocated_hours'], 2),
                'available_hours': round(data['available_hours'], 2),
                'project_hours': round(data['project_hours'], 2),
                'ticket_hours': round(data['ticket_hours'], 2),
                'utilization_percentage': round(utilization, 2),
                'average_efficiency': round(avg_efficiency, 2),
                'activity_count': len(data['activities'])
            })
        
        # Calculate overall statistics
        total_allocated = sum(m['allocated_hours'] for m in monthly_summary)
        total_available = sum(m['available_hours'] for m in monthly_summary)
        total_hours = total_allocated + total_available
        total_working_days = sum(m['working_days'] for m in monthly_summary)
        
        overall_stats = {
            'total_period_days': (end_date - start_date).days,
            'total_working_days': total_working_days,
            'total_hours': round(total_hours, 2),
            'total_allocated_hours': round(total_allocated, 2),
            'total_available_hours': round(total_available, 2),
            'overall_utilization': round((total_allocated / total_hours * 100), 2) if total_hours > 0 else 0,
            'average_daily_allocation': round(total_allocated / total_working_days, 2) if total_working_days > 0 else 0,
            'total_activities': len(detailed_activities)
        }
        
        return {
            'employee_info': {
                'name': f"{employee.first_name} {employee.last_name}",
                'email': employee.email,
                'role': employee.role
            },
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'months_back': months_back,
                'months_forward': months_forward
            },
            'overall_statistics': overall_stats,
            'monthly_summary': monthly_summary,
            'detailed_activities': detailed_activities,
            'report_generated': timezone.now()
        }
    
    @classmethod
    def sync_activity_logs(cls, employee_id=None):
        """
        Synchronize UserActivityLog with Activity model data.
        
        Args:
            employee_id: If provided, sync only for this employee
        """
        if employee_id:
            employees = Ressource.objects.filter(id=employee_id)
        else:
            employees = Ressource.objects.all()
        
        for employee in employees:
            # Get all activities for this employee
            activities = Activity.objects.filter(employee=employee)
            
            for activity in activities:
                # Create or update activity logs
                activity_date = activity.start_datetime.date()
                start_hour = activity.start_datetime.hour
                end_hour = activity.end_datetime.hour
                
                # Handle activities that span multiple hours
                current_hour = start_hour
                while current_hour < end_hour:
                    UserActivityLog.objects.update_or_create(
                        employee=employee,
                        activity=activity,
                        date=activity_date,
                        start_hour=current_hour,
                        defaults={
                            'end_hour': current_hour + 1,
                            'duration_hours': 1.0,
                            'log_type': 'SCHEDULED' if activity_date > timezone.now().date() else 'COMPLETED',
                            'allocation_status': 'ALLOCATED',
                            'project_id': activity.project.id if activity.project else None,
                            'ticket_id': activity.ticket.id if activity.ticket else None,
                            'activity_title': activity.title,
                            'planned_hours': 1.0,
                            'actual_hours': 1.0 if activity_date <= timezone.now().date() else None
                        }
                    )
                    current_hour += 1