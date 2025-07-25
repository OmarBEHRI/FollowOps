from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('ressources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ressource',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
        migrations.AddField(
            model_name='ressource',
            name='completed_tickets_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ressource',
            name='completed_projects_count',
            field=models.IntegerField(default=0),
        ),
    ]