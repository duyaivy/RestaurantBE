#!/bin/bash
set -euo pipefail

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-restaurantBE.settings.production}"
export ENV="${ENV:-prod}"

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

if [ -n "${CHATBOT_CHROMA_DIR:-}" ]; then
    mkdir -p "$CHATBOT_CHROMA_DIR"
fi

# Decode Google credentials from base64 if provided
if [ -n "${GOOGLE_CREDENTIALS_JSON_BASE64:-}" ]; then
    GCP_CREDENTIALS_PATH="/tmp/gcp-sa.json"
    printf '%s' "${GOOGLE_CREDENTIALS_JSON_BASE64}" | base64 -d > "${GCP_CREDENTIALS_PATH}"
    chmod 600 "${GCP_CREDENTIALS_PATH}"
    export GOOGLE_APPLICATION_CREDENTIALS="${GCP_CREDENTIALS_PATH}"
    echo "[Entrypoint] Google credentials decoded successfully."
fi

# Wait for database readiness if host is provided
echo "[Entrypoint] Checking database readiness..."
python - << 'EOF'
import os
import time
from urllib.parse import urlparse

db_url = os.getenv("DATABASE_URL")
host = None
port = 5432

if db_url:
    parsed = urlparse(db_url)
    host = parsed.hostname
    port = parsed.port or 5432
else:
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT", 5432))

if host:
    import socket
    print(f"[Entrypoint] Waiting for database at {host}:{port}...")
    start_time = time.time()
    connected = False
    while time.time() - start_time < 30:
        try:
            s = socket.create_connection((host, int(port)), timeout=2)
            s.close()
            connected = True
            print(f"[Entrypoint] Database ({host}:{port}) is ready!")
            break
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(1)
    if not connected:
        print("[Entrypoint] Warning: Timed out waiting for database. Proceeding anyway...")
EOF

echo "[Entrypoint] Applying database migrations..."
python manage.py migrate --noinput

if command -v msgfmt > /dev/null 2>&1; then
    echo "[Entrypoint] Compiling translation messages..."
    python manage.py compilemessages 2>/dev/null || true
fi

echo "[Entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

LOG_LEVEL="${LOG_LEVEL:-info}"
echo "[Entrypoint] Starting server on port ${PORT:-8000}..."
exec uvicorn restaurantBE.asgi:application \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-1}" \
    --log-level "${LOG_LEVEL,,}"
