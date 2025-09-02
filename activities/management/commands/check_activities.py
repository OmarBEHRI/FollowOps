from django.core.management.base import BaseCommand
from activities.models import Activity
from projects.models import Project

class Command(BaseCommand):
    help = 'Check activities in the database for debugging'

    def handle(self, *args, **options):
        self.stdout.write('=== ACTIVITY DEBUG CHECK ===')
        self.stdout.write(f'Total activities: {Activity.objects.count()}')
        self.stdout.write(f'Project activities: {Activity.objects.filter(activity_type="PROJECT").count()}')
        
        project = Project.objects.first()
        self.stdout.write(f'First project: {project.title if project else "No projects"}')
        
        if project:
            activities = Activity.objects.filter(project=project)
            self.stdout.write(f'Activities for first project ({project.title}): {activities.count()}')
            for i, a in enumerate(activities[:5]):
                self.stdout.write(f'  {i+1}. {a.title}: {a.start_datetime} to {a.end_datetime}')
                self.stdout.write(f'     Employee: {a.employee.first_name} {a.employee.last_name}')
                self.stdout.write(f'     Type: {a.activity_type}')
                self.stdout.write('')
        
        # Check all projects and their activities
        self.stdout.write('\n=== ALL PROJECTS AND ACTIVITIES ===')
        for project in Project.objects.all()[:3]:
            activities = Activity.objects.filter(project=project)
            self.stdout.write(f'Project: {project.title} - {activities.count()} activities')
            for a in activities[:2]:
                self.stdout.write(f'  - {a.title} ({a.start_datetime.date()})')