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
    
    # Define base project templates
    project_templates = [
        {
            'title': 'Refonte du site web',
            'description': 'Refonte complète du site web de l\'entreprise avec un nouveau design et de nouvelles fonctionnalités.',
            'type': 'BUILD',
            'status': 'En cours',
            'priority': 'Haute',
            'estimated_charges': 45,
            'progress': 40,
            'budget': 75000.00,
            'tags': ['Développement', 'Design', 'Client']
        },
        {
            'title': 'Migration vers le cloud',
            'description': 'Migration de l\'infrastructure vers AWS pour améliorer la scalabilité et la fiabilité.',
            'type': 'BUILD',
            'status': 'À initier',
            'priority': 'Critique',
            'estimated_charges': 60,
            'progress': 0,
            'budget': 120000.00,
            'tags': ['Infrastructure', 'Interne']
        },
        {
            'title': 'Application mobile',
            'description': 'Développement d\'une application mobile pour les clients permettant de suivre leurs commandes.',
            'type': 'BUILD',
            'status': 'En cours',
            'priority': 'Moyenne',
            'estimated_charges': 50,
            'progress': 65,
            'budget': 85000.00,
            'tags': ['Développement', 'Client', 'Innovation']
        },
        {
            'title': 'Maintenance des serveurs',
            'description': 'Maintenance régulière des serveurs de production pour assurer leur bon fonctionnement.',
            'type': 'RUN',
            'status': 'En cours',
            'priority': 'Basse',
            'estimated_charges': 20,
            'progress': 30,
            'budget': 25000.00,
            'tags': ['Maintenance', 'Infrastructure']
        },
        {
            'title': 'Formation des nouveaux employés',
            'description': 'Programme de formation pour les nouveaux employés sur les outils et processus de l\'entreprise.',
            'type': 'RUN',
            'status': 'Terminé',
            'priority': 'Moyenne',
            'estimated_charges': 15,
            'progress': 100,
            'budget': 18000.00,
            'tags': ['Formation', 'Interne']
        },
        {
            'title': 'Optimisation de la base de données',
            'description': 'Amélioration des performances de la base de données et optimisation des requêtes.',
            'type': 'BUILD',
            'status': 'Terminé',
            'priority': 'Haute',
            'estimated_charges': 30,
            'progress': 100,
            'budget': 45000.00,
            'tags': ['Infrastructure', 'Développement']
        },
        {
            'title': 'Campagne marketing digital',
            'description': 'Lancement d\'une campagne marketing sur les réseaux sociaux et Google Ads.',
            'type': 'RUN',
            'status': 'En cours',
            'priority': 'Moyenne',
            'estimated_charges': 25,
            'progress': 55,
            'budget': 35000.00,
            'tags': ['Marketing', 'Client']
        },
        {
            'title': 'Système de sauvegarde automatique',
            'description': 'Mise en place d\'un système de sauvegarde automatique pour toutes les données critiques.',
            'type': 'BUILD',
            'status': 'Suspendu',
            'priority': 'Critique',
            'estimated_charges': 40,
            'progress': 20,
            'budget': 60000.00,
            'tags': ['Infrastructure', 'Maintenance']
        }
    ]
    
    # Generate projects with dates spanning from September 2024 to September 2025
    start_date_range = datetime(2024, 9, 2, tzinfo=timezone.get_current_timezone())
    end_date_range = datetime(2025, 9, 2, tzinfo=timezone.get_current_timezone())
    
    projects_data = []
    
    # Create 12-15 projects using templates and variations
    for i in range(12):
        template = project_templates[i % len(project_templates)]
        
        # Generate random creation date within the year span
        days_in_range = (end_date_range - start_date_range).days
        random_days = random.randint(0, days_in_range - 60)  # Leave 60 days for project duration
        creation_date = start_date_range + timedelta(days=random_days)
        
        # Generate project duration (30-120 days)
        project_duration = random.randint(30, 120)
        expected_start_offset = random.randint(-10, 30)  # Can start before or after creation
        
        expected_start = creation_date + timedelta(days=expected_start_offset)
        expected_end = expected_start + timedelta(days=project_duration)
        
        # Determine actual start and end dates based on status
        start_date = None
        end_date = None
        
        if template['status'] in ['En cours', 'Terminé', 'Suspendu']:
            start_date = expected_start + timedelta(days=random.randint(-5, 15))
            start_date = start_date.date() if hasattr(start_date, 'date') else start_date
            
        if template['status'] == 'Terminé':
            end_date = start_date + timedelta(days=random.randint(int(project_duration * 0.8), int(project_duration * 1.2)))
            # Ensure end date is not in the future
            if end_date > timezone.now().date():
                end_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
            else:
                end_date = end_date.date() if hasattr(end_date, 'date') else end_date
        
        # Add variation to title for uniqueness
        title_variations = ['', ' v2', ' Phase 1', ' Phase 2', ' - Amélioration', ' - Extension']
        title = template['title'] + random.choice(title_variations)
        
        project_data = {
            'title': title,
            'description': template['description'],
            'type': template['type'],
            'status': template['status'],
            'priority': template['priority'],
            'expected_start_date': expected_start.date(),
            'expected_end_date': expected_end.date(),
            'start_date': start_date if start_date else None,
            'end_date': end_date if end_date else None,
            'estimated_charges': template['estimated_charges'] + random.randint(-10, 10),
            'progress': template['progress'] + random.randint(-20, 20) if template['progress'] > 0 else 0,
            'budget': template['budget'] + random.randint(-10000, 10000),
            'tags': template['tags'],
            'created_at': creation_date
        }
        
        # Ensure progress is within bounds
        project_data['progress'] = max(0, min(100, project_data['progress']))
        
        projects_data.append(project_data)
    
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
            progress=project_data['progress'],
            budget=project_data['budget']
        )
        
        # Set the created_at field to the specified date
        project.created_at = project_data['created_at']
        project.save()
        
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
            
            # Add 5-10 activities per project, focusing on September 2025 for better UI testing
            num_activities = random.randint(5, 10)
            for _ in range(num_activities):
                # Focus on September 2025 for current month visibility
                september_start = datetime(2025, 9, 1).date()
                september_end = datetime(2025, 9, 30).date()
                
                # 70% chance for September 2025, 30% for other dates
                if random.random() < 0.7:
                    # September 2025 activities
                    activity_date = september_start + timedelta(days=random.randint(0, 29))
                else:
                    # Other dates within project timeframe
                    if project.end_date:
                        activity_date = project.start_date + timedelta(days=random.randint(0, (project.end_date - project.start_date).days))
                    else:
                        activity_date = project.start_date + timedelta(days=random.randint(0, (timezone.now().date() - project.start_date).days))
                
                # Make sure it's a weekday (0-4 is Monday to Friday)
                while activity_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                    activity_date = activity_date + timedelta(days=1)
                    # If we go past September, wrap back to the beginning
                    if activity_date > september_end and activity_date.month == 10:
                        activity_date = september_start + timedelta(days=random.randint(0, 6))
                
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