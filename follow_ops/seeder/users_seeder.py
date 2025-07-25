import random
from datetime import datetime, timedelta
from django.utils import timezone
from ressources.models import Ressource

def seed_users():
    """
    Create initial users for the application.
    Returns a list of created users.
    """
    # Check if users already exist to avoid duplicates
    User = Ressource
    if User.objects.filter(email='admin@followops.com').exists():
        print("Users already exist, skipping user creation")
        return list(User.objects.all())
    # Define Arab first names and last names for realistic data
    arab_first_names = [
        'Mohammed', 'Ahmed', 'Ali', 'Omar', 'Youssef', 'Ibrahim', 'Mustafa', 'Hassan',
        'Khalid', 'Abdullah', 'Samir', 'Tariq', 'Adel', 'Karim', 'Jamal', 'Nasser',
        'Walid', 'Mahmoud', 'Faisal', 'Ziad', 'Fatima', 'Aisha', 'Layla', 'Noor',
        'Amina', 'Mariam', 'Zahra', 'Huda', 'Zainab', 'Samira', 'Leila', 'Rania',
        'Yasmin', 'Sara', 'Nadia', 'Dalia', 'Farida', 'Salma', 'Rana', 'Hanan'
    ]
    
    arab_last_names = [
        'Alami', 'Benjelloun', 'Tazi', 'Fassi', 'Idrissi', 'Berrada', 'Bennani', 'Chraibi',
        'Lahlou', 'Tahiri', 'Amrani', 'Benhima', 'Cherkaoui', 'Ouazzani', 'Sebti', 'Bennis',
        'Kadiri', 'Lazrak', 'Belghiti', 'Bensouda', 'Kettani', 'Sqalli', 'Filali', 'Laraki',
        'Benchekroun', 'Benkirane', 'Lahlimi', 'Lemfedel', 'Skalli', 'Alaoui', 'Bennani', 'Chami',
        'Drissi', 'El Fassi', 'Ghali', 'Hajji', 'Iraqi', 'Jalal', 'Karimi', 'Lamrani'
    ]
    
    # Define user data
    users_data = [
        {
            'email': 'admin@followops.com',
            'username': 'admin',
            'password': 'admin123',
            'first_name': 'Mohammed',
            'last_name': 'Al-Rashid',
            'role': 'Directeur',
            'skills': 'Management, Leadership, Strategy',
            'availability_rate': 100,
            'status': 'CDI',
            'appRole': 'ADMIN',
            'phone_number': '0123456789',
            'entry_date': timezone.now().date() - timedelta(days=365*2),
            'location': 'Paris'
        },
        {
            'email': 'manager@followops.com',
            'username': 'manager',
            'password': 'manager123',
            'first_name': 'Fatima',
            'last_name': 'Al-Najjar',
            'role': 'Chef de projet',
            'skills': 'Project Management, Agile, Scrum',
            'availability_rate': 80,
            'status': 'CDI',
            'appRole': 'MANAGER',
            'phone_number': '0123456790',
            'entry_date': timezone.now().date() - timedelta(days=365),
            'location': 'Lyon'
        },
    ]
    
    # Add regular users
    roles = ['Développeur', 'Designer', 'Testeur', 'Analyste', 'DevOps']
    skills_by_role = {
        'Développeur': ['Python', 'JavaScript', 'Java', 'C#', 'PHP', 'React', 'Angular', 'Vue.js', 'Django', 'Flask'],
        'Designer': ['UI/UX', 'Figma', 'Adobe XD', 'Photoshop', 'Illustrator', 'Sketch', 'InDesign'],
        'Testeur': ['Test unitaire', 'Test d\'intégration', 'Test fonctionnel', 'Selenium', 'JUnit', 'TestNG', 'Cypress'],
        'Analyste': ['Analyse de données', 'SQL', 'Business Intelligence', 'Tableau', 'Power BI', 'Excel avancé'],
        'DevOps': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'CI/CD', 'Jenkins', 'Ansible', 'Terraform']
    }
    statuses = ['CDI', 'CDD', 'Stagiaire', 'Alternant', 'Prestataire']
    locations = ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille', 'Toulouse', 'Nantes', 'Strasbourg']
    
    # Generate 10 regular users
    for i in range(1, 11):
        role = random.choice(roles)
        skills_list = random.sample(skills_by_role[role], min(3, len(skills_by_role[role])))
        
        # Select random first and last names
        first_name = random.choice(arab_first_names)
        last_name = random.choice(arab_last_names)
        
        users_data.append({
            'email': f'user{i}@followops.com',
            'username': f'user{i}',
            'password': f'user{i}123',
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'skills': ', '.join(skills_list),
            'availability_rate': random.randint(50, 100),
            'status': random.choice(statuses),
            'appRole': 'USER',
            'phone_number': f'01234567{i:02d}',
            'entry_date': timezone.now().date() - timedelta(days=random.randint(30, 730)),
            'location': random.choice(locations)
        })
    
    # Create users in the database
    created_users = []
    for user_data in users_data:
        user = Ressource.objects.create_user(
            email=user_data['email'],
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            skills=user_data['skills'],
            availability_rate=user_data['availability_rate'],
            status=user_data['status'],
            appRole=user_data['appRole'],
            phone_number=user_data['phone_number'],
            entry_date=user_data['entry_date'],
            location=user_data['location']
        )
        created_users.append(user)
    
    # Set manager relationships
    admin_user = Ressource.objects.get(email='admin@followops.com')
    manager_user = Ressource.objects.get(email='manager@followops.com')
    
    # Admin is the manager of the manager
    manager_user.manager = admin_user
    manager_user.save()
    
    # Manager is the manager of regular users
    for user in Ressource.objects.filter(appRole='USER'):
        user.manager = manager_user
        user.save()
    
    return created_users