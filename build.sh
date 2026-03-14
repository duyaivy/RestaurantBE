#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn --bind 0.0.0.0:${PORT:-10000} --access-logfile - --error-logfile - restaurantBE.wsgi:application
