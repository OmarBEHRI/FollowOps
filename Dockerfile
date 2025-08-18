# Use official Python image
FROM python:3.11-slim

# Set environment variables (no .pyc files, unbuffered logs)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside the container
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /code/

# Expose Django's default port
EXPOSE 8000

# Create a startup script to run migrations before starting the server
COPY <<EOF /code/start.sh
#!/bin/bash
echo "Waiting for database to be ready..."
sleep 5
echo "Running makemigrations..."
python manage.py makemigrations
echo "Running migrations..."
python manage.py migrate
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
EOF

RUN chmod +x /code/start.sh

# Default command
CMD ["/bin/bash", "/code/start.sh"]
