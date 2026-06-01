#!/bin/bash
set -euo pipefail

# Decode Google credentials from base64 if provided
if [ -n "${GOOGLE_CREDENTIALS_JSON_BASE64:-}" ]; then
    GCP_CREDENTIALS_PATH="/tmp/gcp-sa.json"
    printf '%s' "${GOOGLE_CREDENTIALS_JSON_BASE64}" | base64 -d > "${GCP_CREDENTIALS_PATH}"
    chmod 600 "${GCP_CREDENTIALS_PATH}"
    export GOOGLE_APPLICATION_CREDENTIALS="${GCP_CREDENTIALS_PATH}"
    echo "Google credentials decoded."
fi

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "Starting server on port ${PORT:-8000}..."
exec uvicorn restaurantBE.asgi:application \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --log-level "${LOG_LEVEL:-info}"
