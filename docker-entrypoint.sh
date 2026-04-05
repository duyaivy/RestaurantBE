#!/bin/bash

set -euo pipefail

if [ -n "${GOOGLE_CREDENTIALS_JSON_BASE64:-}" ]; then
	GCP_CREDENTIALS_PATH="/tmp/gcp-sa.json"
	if command -v base64 >/dev/null 2>&1; then
		printf '%s' "${GOOGLE_CREDENTIALS_JSON_BASE64}" | base64 -d > "${GCP_CREDENTIALS_PATH}"
	else
		echo "base64 command not found" >&2
		exit 1
	fi
	chmod 600 "${GCP_CREDENTIALS_PATH}"
	export GOOGLE_APPLICATION_CREDENTIALS="${GCP_CREDENTIALS_PATH}"
fi

echo "Make migrations"
python manage.py makemigrations

echo "Apply database migrations"
python manage.py migrate

echo "Seed database"
python manage.py loaddata restaurantBE/database/seed.json || echo "Seed data not found or already loaded"

echo "Starting server on port ${PORT:-80}"
gunicorn --bind 0.0.0.0:${PORT:-80} --access-logfile - --error-logfile - restaurantBE.wsgi
