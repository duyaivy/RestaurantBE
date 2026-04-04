#!/usr/bin/env bash
# exit on error
set -o errexit

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

python manage.py migrate
if command -v msgfmt >/dev/null 2>&1; then
	python manage.py compilemessages
else
	echo "[i18n] msgfmt not found, skip compilemessages"
fi
python manage.py collectstatic --no-input

if python -c "import fcntl" >/dev/null 2>&1 && command -v gunicorn >/dev/null 2>&1; then
	gunicorn --bind 0.0.0.0:${PORT:-10000} --access-logfile - --error-logfile - restaurantBE.wsgi:application
else
	echo "[startup] gunicorn is not available on this platform, fallback to Django runserver"
	python manage.py runserver 0.0.0.0:${PORT:-10000}
fi
