# FollowOps

A comprehensive project management and resource tracking system built with Django and Docker.

## Features

- **User Management**: Complete user authentication and profile management
- **Project Management**: Create, edit, and manage projects with detailed information
- **Resource Management**: Track and manage human resources with profiles and assignments
- **Ticket System**: Create and manage tickets for project tasks and issues
- **Activity Tracking**: Monitor project activities and progress
- **Dashboard**: Comprehensive dashboards for users and managers
- **Calendar Integration**: Project and resource calendar views

## Technology Stack

- **Backend**: Django 5.2
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker & Docker Compose
- **Dependencies**: Pandas, Pillow, Cryptography, PyMySQL

## Project Structure

```
FollowOps/
├── activities/          # Activity tracking app
├── dashboard/           # Dashboard views and templates
├── follow_ops/          # Main Django project settings
├── homepage/            # Homepage app
├── projects/            # Project management app
├── ressources/          # Resource management app
├── seeder/              # Database seeding utilities
├── tickets/             # Ticket management app
├── public/              # Static assets
├── staticfiles/         # Collected static files
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker container configuration
└── requirements.txt     # Python dependencies
```

## Running the Project with Docker Compose

### Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

### Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd FollowOps
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Django application container
   - Start the MySQL database container
   - Automatically run database migrations
   - Seed the database with initial data
   - Start the Django development server

3. **Access the application**:
   - Open your browser and navigate to: `http://localhost:8000`
   - The application will be ready to use

### Docker Compose Commands

#### Starting the Application
```bash
# Start in foreground (recommended for development)
docker-compose up

# Start in background
docker-compose up -d

# Rebuild containers and start
docker-compose up --build
```

#### Stopping the Application
```bash
# Stop running containers
docker-compose down

# Stop and remove volumes (WARNING: This will delete database data)
docker-compose down -v
```

#### Managing the Database

**Important**: Migrations run automatically when containers start, so you typically don't need to run them manually.

```bash
# Run migrations manually (if needed)
docker-compose exec web python manage.py migrate

# Create new migrations
docker-compose exec web python manage.py makemigrations

# Access Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

#### Viewing Logs
```bash
# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs web
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f
```

### Database Persistence

- Database data is persisted in a Docker volume named `followops_mysql_data`
- Data will persist between container restarts
- To reset the database completely, use: `docker-compose down -v`

### Default Credentials

The application comes with seeded data including:
- Admin user: `admin@followops.com`
- Password: `admin123`
- Sample projects, resources, and tickets


### Development Workflow

1. **Make code changes**: Edit files in your local directory
2. **Restart if needed**: Most changes are reflected immediately due to Django's auto-reload
3. **For dependency changes**: Rebuild containers with `docker-compose up --build`
4. **For database changes**: Migrations run automatically on container start

### Production Considerations

- Change `DEBUG = False` in Django settings
- Use a production WSGI server instead of Django's development server
- Configure proper environment variables for sensitive data
- Use external database service for production
- Set up proper logging and monitoring
