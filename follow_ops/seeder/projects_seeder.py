import random
from datetime import datetime, timedelta
from django.utils import timezone
from projects.models import Project, Tag, CommentProject
from activities.models import Activity
from ressources.models import Ressource

def seed_projects(users):
    """
    Create initial projects for the application.
    Returns a list of created projects.
    """
    # Create some tags first
    tags_data = [
        'Développement', 'Design', 'Marketing', 'Infrastructure', 'Maintenance',
        'Urgent', 'Innovation', 'Client', 'Interne', 'Formation'
    ]
    
    tags = []
    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)
    
    # Define project data
    projects_data = [
        {
            'title': 'Refonte du site web',
            'description': 'Refonte complète du site web de l\'entreprise avec un nouveau design et de nouvelles fonctionnalités.',
            'type': 'BUILD',
            'status': 'En cours',
            'priority': 'Haute',
            'expected_start_date': timezone.now().date() - timedelta(days=30),
            'expected_end_date': timezone.now().date() + timedelta(days=60),
            'start_date': timezone.now().date() - timedelta(days=25),
            'end_date': None,
            'estimated_charges': 45,
            'progress': 40,
            'tags': ['Développement', 'Design', 'Client']
        },
        {
            'title': 'Migration vers le cloud',
            'description': 'Migration de l\'infrastructure vers AWS pour améliorer la scalabilité et la fiabilité.',
            'type': 'BUILD',
            'status': 'À initier',
            'priority': 'Critique',
            'expected_start_date': timezone.now().date() + timedelta(days=15),
            'expected_end_date': timezone.now().date() + timedelta(days=75),
            'start_date': None,
            'end_date': None,
            'estimated_charges': 60,
            'progress': 0,
            'tags': ['Infrastructure', 'Interne']
        },
        {
            'title': 'Application mobile',
            'description': 'Développement d\'une application mobile pour les clients permettant de suivre leurs commandes.',
            'type': 'BUILD',
            'status': 'En cours',
            'priority': 'Moyenne',
            'expected_start_date': timezone.now().date() - timedelta(days=45),
            'expected_end_date': timezone.now().date() + timedelta(days=30),
            'start_date': timezone.now().date() - timedelta(days=40),
            'end_date': None,
            'estimated_charges': 50,
            'progress': 65,
            'tags': ['Développement', 'Client', 'Innovation']
        },
        {
            'title': 'Maintenance des serveurs',
            'description': 'Maintenance régulière des serveurs de production pour assurer leur bon fonctionnement.',
            'type': 'RUN',
            'status': 'En cours',
            'priority': 'Basse',
            'expected_start_date': timezone.now().date() - timedelta(days=90),
            'expected_end_date': timezone.now().date() + timedelta(days=275),
            'start_date': timezone.now().date() - timedelta(days=90),
            'end_date': None,
            'estimated_charges': 20,
            'progress': 30,
            'tags': ['Maintenance', 'Infrastructure']
        },
        {
            'title': 'Formation des nouveaux employés',
            'description': 'Programme de formation pour les nouveaux employés sur les outils et processus de l\'entreprise.',
            'type': 'RUN',
            'status': 'Terminé',
            'priority': 'Moyenne',
            'expected_start_date': timezone.now().date() - timedelta(days=60),
            'expected_end_date': timezone.now().date() - timedelta(days=30),
            'start_date': timezone.now().date() - timedelta(days=58),
            'end_date': timezone.now().date() - timedelta(days=28),
            'estimated_charges': 15,
            'progress': 100,
            'tags': ['Formation', 'Interne']
        }
    ]
    
    # Get manager users for project managers
    managers = [user for user in users if user.appRole in ['ADMIN', 'MANAGER']]
    
    # Create projects
    created_projects = []
    for project_data in projects_data:
        # Create project
        project = Project.objects.create(
            title=project_data['title'],
            description=project_data['description'],
            type=project_data['type'],
            status=project_data['status'],
            priority=project_data['priority'],
            project_manager=random.choice(managers),
            expected_start_date=project_data['expected_start_date'],
            expected_end_date=project_data['expected_end_date'],
            start_date=project_data['start_date'],
            end_date=project_data['end_date'],
            estimated_charges=project_data['estimated_charges'],
            progress=project_data['progress']
        )
        
        # Add tags
        for tag_name in project_data['tags']:
            tag = Tag.objects.get(name=tag_name)
            project.tags.add(tag)
        
        # Add random members (3-6 members per project)
        num_members = random.randint(3, min(6, len(users)))
        project_members = random.sample(users, num_members)
        for member in project_members:
            project.members.add(member)
        
        created_projects.append(project)
    
    return created_projects

def seed_project_activities_comments(users, projects):
    """
    Add activities and comments to projects.
    """
    # Add comments to projects
    comment_templates = [
        "Bonne progression sur ce projet.",
        "Nous devons accélérer le rythme pour respecter les délais.",
        "Excellente collaboration de l'équipe sur ce projet.",
        "Quelques difficultés techniques à résoudre rapidement.",
        "Le client est très satisfait de l'avancement.",
        "Réunion de suivi prévue la semaine prochaine.",
        "Besoin de ressources supplémentaires pour ce projet.",
        "Phase de test à planifier prochainement.",
        "Documentation à mettre à jour avant la livraison.",
        "Risques identifiés à mitiger rapidement."
    ]
    
    for project in projects:
        # Skip adding comments to projects that haven't started yet
        if not project.start_date:
            continue
            
        # Add 2-5 comments per project
        num_comments = random.randint(2, 5)
        for _ in range(num_comments):
            comment = CommentProject.objects.create(
                project=project,
                content=random.choice(comment_templates),
                author=random.choice(users)
            )
            project.comments.add(comment)
        
        # Add activities for projects that have started
        if project.start_date:
            # Get project members
            members = list(project.members.all())
            
            # Add 3-8 activities per project
            num_activities = random.randint(3, 8)
            for _ in range(num_activities):
                # Random date within project timeframe
                if project.end_date:
                    activity_date = project.start_date + timedelta(days=random.randint(0, (project.end_date - project.start_date).days))
                else:
                    activity_date = project.start_date + timedelta(days=random.randint(0, (timezone.now().date() - project.start_date).days))
                
                # Make sure it's a weekday (0-4 is Monday to Friday)
                while activity_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                    activity_date = activity_date + timedelta(days=1)
                
                # Random start time between 9:00 and 15:00
                start_hour = random.randint(9, 15)
                start_minute = random.choice([0, 15, 30, 45])
                
                # Random duration between 1-3 hours
                duration_hours = random.randint(1, 3)
                
                # Create activity datetime objects
                start_datetime = datetime.combine(activity_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
                start_datetime = timezone.make_aware(start_datetime)
                end_datetime = start_datetime + timedelta(hours=duration_hours)
                
                # Create activity
                activity_titles = [
                    "Réunion de suivi",
                    "Développement de fonctionnalité",
                    "Revue de code",
                    "Test d'intégration",
                    "Documentation",
                    "Conception",
                    "Déploiement",
                    "Formation"
                ]
                
                Activity.objects.create(
                    title=random.choice(activity_titles),
                    description=f"Activité sur le projet {project.title}",
                    employee=random.choice(members),
                    activity_type="PROJECT",
                    project=project,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime
                )