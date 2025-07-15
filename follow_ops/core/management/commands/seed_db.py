import random
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from ressources.models import Ressource
from projects.models import Project, Tag
from tickets.models import Ticket, Comment
from faker import Faker

fake = Faker('fr_FR')  # Using French locale for realistic French names

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        if Ressource.objects.exists():
            self.stdout.write(self.style.SUCCESS('Database already seeded. Skipping...'))
            return

        self.stdout.write('Seeding database...')
        
        # Create Tags
        tags = []
        tag = Tag.objects.create(name='Web')
        tags.append(tag)

        tag = Tag.objects.create(name='Mobile')
        tags.append(tag)

        tag = Tag.objects.create(name='Desktop')
        tags.append(tag)

        tag = Tag.objects.create(name='Système')
        tags.append(tag)

        tag = Tag.objects.create(name='Sécurité')
        tags.append(tag)

        tag = Tag.objects.create(name='Réseau')
        tags.append(tag)

        tag = Tag.objects.create(name='Cloud')
        tags.append(tag)

        tag = Tag.objects.create(name='Big Data')
        tags.append(tag)

        tag = Tag.objects.create(name='Artificielle')
        tags.append(tag)

        tag = Tag.objects.create(name='Intelligence')
        tags.append(tag)
        
        # Create Resources
        managers = []
        for _ in range(3):
            manager = Ressource.objects.create(
                username=fake.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='Manager',
                status='CDI',
                phone_number=fake.phone_number()[:20],
                location=fake.city(),
                password=make_password('password123')
            )
            managers.append(manager)

        members = []
        for _ in range(10):
            member = Ressource.objects.create(
                username=fake.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=random.choice(['Développeur', 'Designer', 'Chef de projet', 'Testeur']),
                status=random.choice(['CDI', 'CDD', 'Prestataire']),
                phone_number=fake.phone_number()[:20],
                location=fake.city(),
                password=make_password('password123')
            )
            members.append(member)

        # Create Projects
        projects = []
        for i in range(5):
            project = Project.objects.create(
                title=f"Projet {fake.word().capitalize()} {i+1}",
                description=fake.paragraph(),
                type=random.choice(['BUILD', 'RUN']),
                status=random.choice(['À initier', 'En cours', 'Terminé', 'Suspendu']),
                priority=random.choice(['Basse', 'Moyenne', 'Haute', 'Critique']),
                project_manager=random.choice(managers),
                expected_start_date=fake.future_date(),
                expected_end_date=fake.future_date(end_date='+1y'),
                estimated_charges=random.randint(100, 1000),
                progress=random.randint(0, 100)
            )
            project.members.set(random.sample(members, k=random.randint(2, 5)))
            project.tags.set(random.sample(tags, k=random.randint(1, 3)))
            projects.append(project)

        # Create Tickets
        for _ in range(20):
            ticket = Ticket.objects.create(
                title=f"Ticket {fake.word().capitalize()}",
                description=fake.paragraph(),
                assigned_to=random.choice(members),
                status=random.choice(['Ouvert', 'En cours', 'Fermé']),
                project=random.choice(projects)
            )
            
            # Add comments to tickets
            for _ in range(random.randint(1, 3)):
                Comment.objects.create(
                    ticket=ticket,
                    content=fake.sentence(),
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))