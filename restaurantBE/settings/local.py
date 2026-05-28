"""
Settings for local development environment.
"""

from urllib.parse import urlparse, parse_qsl
from .common import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = True

SECRET_KEY = "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"

ALLOWED_HOSTS = ["*"]

HOST = os.getenv("HOST", "http://localhost:8000/")

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

database_url = os.getenv("DATABASE_URL") or ""
tmpPostgres = urlparse(database_url)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": tmpPostgres.path.replace("/", "") if tmpPostgres.path else "",
        "USER": tmpPostgres.username,
        "PASSWORD": tmpPostgres.password,
        "HOST": tmpPostgres.hostname,
        "PORT": 5432,
        "OPTIONS": dict(parse_qsl(tmpPostgres.query)) if tmpPostgres.query else {},
    }
}

# CORS
_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").strip()
if _cors_origins == "*":
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
else:
    CORS_ALLOWED_ORIGINS = [
        origin.strip() for origin in _cors_origins.split(",") if origin.strip()
    ]

_valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in _valid_levels:
    LOG_LEVEL = "INFO"

DB_LOG_LEVEL = os.getenv("DJANGO_DB_LOG_LEVEL", "WARNING").upper()
if DB_LOG_LEVEL not in _valid_levels:
    DB_LOG_LEVEL = "WARNING"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {filename}:{lineno} >>> {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.db": {
            "handlers": ["console"],
            "level": DB_LOG_LEVEL,
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": DB_LOG_LEVEL,
            "propagate": False,
        },
    },
}
