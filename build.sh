#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load seed data (optional - comment out if not needed)
# python manage.py loaddata restaurantBE/database/seed.json
