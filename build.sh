#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
if command -v msgfmt >/dev/null 2>&1; then
	python manage.py compilemessages
else
	echo "[i18n] msgfmt not found, skip compilemessages"
fi
python manage.py collectstatic --no-input
gunicorn --bind 0.0.0.0:${PORT:-10000} --access-logfile - --error-logfile - restaurantBE.wsgi:application
