#!/bin/bash

echo "Make migrations"
python manage.py makemigrations

echo "Apply database migrations"
python manage.py migrate

echo "Seed database"
python manage.py loaddata restaurantBE/database/seed.json || echo "Seed data not found or already loaded"

echo "Starting server on port ${PORT:-80}"
gunicorn --bind 0.0.0.0:${PORT:-80} --access-logfile - --error-logfile - restaurantBE.wsgi
