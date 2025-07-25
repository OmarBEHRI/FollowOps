from django.apps import AppConfig

class SeederConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seeder'
    
    def ready(self):
        """
        This method is called when the application is ready.
        We'll use it to run our database seeding script if needed.
        """
        # Only run in the main process (not in management commands or other subprocesses)
        import os
        if os.environ.get('RUN_MAIN') == 'true':
            # Import and run the seeding function
            from .main import seed_database
            seed_database()