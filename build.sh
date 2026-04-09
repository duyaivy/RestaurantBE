#!/usr/bin/env bash
# exit on error
set -o errexit
set -o pipefail

if [ -n "${GOOGLE_CREDENTIALS_JSON_BASE64:-}" ]; then
	GCP_CREDENTIALS_PATH="/tmp/gcp-sa.json"
	if command -v base64 > /dev/null 2>&1; then
		printf '%s' "${GOOGLE_CREDENTIALS_JSON_BASE64}" | base64 -d > "${GCP_CREDENTIALS_PATH}"
	else
		echo "base64 command not found" >&2
		exit 1
	fi
	chmod 600 "${GCP_CREDENTIALS_PATH}"
	export GOOGLE_APPLICATION_CREDENTIALS="${GCP_CREDENTIALS_PATH}"
fi

python manage.py migrate --no-input
if command -v msgfmt > /dev/null 2>&1; then
	python manage.py compilemessages
else
	echo "[i18n] msgfmt not found, skip compilemessages"
fi
python manage.py collectstatic --no-input

uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port ${PORT:-10000}