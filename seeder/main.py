import os

# Note: Django setup is already handled by the framework when running as an app
# This configuration is only needed when running the script directly

from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

# Import seeder modules
from .users_seeder import seed_users, update_availability_rates
from .projects_seeder import seed_projects, seed_project_activities_comments
from .tickets_seeder import seed_tickets, seed_ticket_activities_comments
from .status_logs_seeder import seed_status_logs

def is_database_seeded():
    """
    Check if the database is already seeded by checking if there are users with specific emails
    that would be created during seeding.
    """
    try:
        User = get_user_model()
        # Check if our seed admin user exists
        return User.objects.filter(email='admin@followops.com').exists()
    except Exception as e:
        # If there's any database error (like table doesn't exist), assume not seeded
        print(f"Database not ready for seeding check: {e}")
        return False

def seed_database():
    """
    Main function to seed the database with initial data.
    This function will check if the database is already seeded before proceeding.
    """
    if is_database_seeded():
        print("Database is already seeded. Skipping seeding process.")
        return False
    
    print("Starting database seeding process...")
    
    try:
        with transaction.atomic():
            # Seed users first as they are required for other entities
            users = seed_users()
            print(f"✅ Created {len(users)} users")
            
            # Seed projects
            projects = seed_projects(users)
            print(f"✅ Created {len(projects)} projects")
            
            # Seed tickets
            tickets = seed_tickets(users, projects)
            print(f"✅ Created {len(tickets)} tickets")
            
            # Add activities and comments to projects
            seed_project_activities_comments(users, projects)
            print("✅ Added activities and comments to projects")
            
            # Add activities and comments to tickets
            seed_ticket_activities_comments(users, tickets)
            print("✅ Added activities and comments to tickets")
            
            # Seed status logs for tickets and projects
            ticket_logs, project_logs = seed_status_logs(users, projects, tickets)
            print(f"✅ Created {len(ticket_logs)} ticket status logs and {len(project_logs)} project status logs")
            
            # Update availability rates based on seeded activities
            update_availability_rates()
            print("✅ Updated availability rates based on activities")
            
        print("✅ Database seeding completed successfully!")
        return True
    
    except IntegrityError as e:
        print(f"❌ Error during database seeding: {e}")
        print("Database seeding failed. Rolling back changes.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during database seeding: {e}")
        print("Database seeding failed. Rolling back changes.")
        return False

# This allows the script to be run directly
if __name__ == "__main__":
    # Configure Django settings when running directly
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'follow_ops.settings')
    django.setup()
    
    seed_database()