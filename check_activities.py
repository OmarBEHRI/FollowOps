from activities.models import Activity
from projects.models import Project

print('=== ACTIVITY DEBUG CHECK ===')
print('Total activities:', Activity.objects.count())
print('Project activities:', Activity.objects.filter(activity_type='PROJECT').count())

project = Project.objects.first()
print('First project:', project.title if project else 'No projects')

if project:
    activities = Activity.objects.filter(project=project)
    print(f'Activities for first project ({project.title}):', activities.count())
    for i, a in enumerate(activities[:5]):
        print(f'  {i+1}. {a.title}: {a.start_datetime} to {a.end_datetime}')
        print(f'     Employee: {a.employee.first_name} {a.employee.last_name}')
        print(f'     Type: {a.activity_type}')
        print()

# Check all projects and their activities
print('\n=== ALL PROJECTS AND ACTIVITIES ===')
for project in Project.objects.all()[:3]:
    activities = Activity.objects.filter(project=project)
    print(f'Project: {project.title} - {activities.count()} activities')
    for a in activities[:2]:
        print(f'  - {a.title} ({a.start_datetime.date()})')