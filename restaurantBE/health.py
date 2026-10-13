"""Readiness checks with useful server logs and no public error details."""
import logging
import os
import re
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


def _safe_error(exc):
    message = str(exc)
    message = re.sub(r"([a-zA-Z][a-zA-Z0-9+.-]*://)[^\s/]*@", r"\1[REDACTED]@", message)
    # Never print connection URLs or environment secrets from exception text.
    for key, value in os.environ.items():
        if value and any(part in key for part in ("PASSWORD", "SECRET", "TOKEN", "API_KEY", "CREDENTIALS")):
            message = message.replace(value, "[REDACTED]")
    secrets = [settings.DATABASES["default"].get("PASSWORD")]
    try:
        secrets.append(urlparse(settings.REDIS_URL).password)
    except ValueError:
        pass
    for value in secrets:
        if value:
            message = message.replace(str(value), "[REDACTED]")
            message = message.replace(unquote(str(value)), "[REDACTED]")
    return message.replace("\n", " ").replace("\r", " ")[:1000]


def _check_database():
    # A cached connection can be stale: execute a query, not just ensure_connection.
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        if cursor.fetchone() != (1,):
            raise RuntimeError("Database SELECT 1 returned an unexpected result")


def _check_redis():
    # Use a separate, bounded probe; don't change the application's cache pool.
    with Redis.from_url(
        settings.REDIS_URL, socket_connect_timeout=3, socket_timeout=3,
        retry=Retry(NoBackoff(), 0),
    ) as client:
        if not client.ping():
            raise RuntimeError("Redis PING did not succeed")


def _check_chroma_storage():
    directory = Path(settings.CHATBOT_CHROMA_DIR or settings.BASE_DIR / "chatbot/rag/.chroma")
    directory.mkdir(parents=True, exist_ok=True)
    # Check actual writes, including disk-full errors, without touching the index.
    with tempfile.NamedTemporaryFile(prefix=".health-", dir=directory) as probe:
        probe.write(b"ok")
        probe.flush()


@api_view(["GET", "HEAD"])
@permission_classes([AllowAny])
def health_check(request):
    started = time.monotonic()
    checks = {}
    for name, check in (
        ("db", _check_database),
        ("redis", _check_redis),
        ("chroma_storage", _check_chroma_storage),
    ):
        check_started = time.monotonic()
        try:
            check()
            checks[name] = "ok"
        except Exception as exc:
            checks[name] = "error"
            logger.error(
                "Health check failed: component=%s exception=%s reason=%s elapsed_ms=%.1f",
                name, type(exc).__name__, _safe_error(exc),
                (time.monotonic() - check_started) * 1000,
            )
            if name == "db":
                # Drop a failed cached connection so the next probe can reconnect.
                try:
                    connection.close()
                except Exception:
                    pass

    healthy = all(value == "ok" for value in checks.values())
    status_code = 200 if healthy else 503
    logger.log(
        logging.INFO if healthy else logging.ERROR,
        "Health check: method=%s host=%s status=%d db=%s redis=%s chroma_storage=%s elapsed_ms=%.1f",
        request.method, request.get_host(), status_code,
        checks["db"], checks["redis"], checks["chroma_storage"],
        (time.monotonic() - started) * 1000,
    )
    return JsonResponse({"status": "ok" if healthy else "error", **checks}, status=status_code)
