# Database Seeder pour FollowOps

## Description

Ce module permet de peupler automatiquement la base de données avec des données initiales pour faciliter le développement et les tests. Le seeding est automatiquement déclenché lors du démarrage du serveur Django avec la commande `runserver`.

## Fonctionnalités

- Création d'utilisateurs avec différents rôles (admin, manager, utilisateurs réguliers)
- Création de projets avec des membres, des tags, des commentaires et des activités
- Création de tickets associés aux projets avec des assignations, des commentaires et des activités
- Vérification préalable pour éviter de repeupler une base de données déjà initialisée

## Structure

- `main.py` : Point d'entrée principal qui coordonne le processus de seeding
- `users_seeder.py` : Création des utilisateurs
- `projects_seeder.py` : Création des projets et de leurs activités/commentaires
- `tickets_seeder.py` : Création des tickets et de leurs activités/commentaires
- `apps.py` : Configuration de l'application Django pour déclencher le seeding au démarrage

## Fonctionnement

Le seeding est automatiquement déclenché lors du démarrage du serveur Django grâce à la méthode `ready()` dans `apps.py`. Le script vérifie d'abord si la base de données est déjà peuplée en recherchant l'utilisateur admin par défaut. Si la base de données est déjà initialisée, le script ne fait rien.

## Données générées

- **Utilisateurs** : Un admin, un manager et 10 utilisateurs réguliers avec différents rôles et compétences
- **Projets** : 5 projets avec différents statuts, priorités et types
- **Tickets** : 2-4 tickets par projet avec différents statuts
- **Activités** : Activités associées aux projets et tickets pour simuler le travail des membres
- **Commentaires** : Commentaires sur les projets et tickets pour simuler les discussions

## Exécution manuelle

Bien que le seeding soit automatique au démarrage du serveur, vous pouvez également l'exécuter manuellement avec la commande suivante :

```python
python manage.py shell -c "from seeder.main import seed_database; seed_database()"
```