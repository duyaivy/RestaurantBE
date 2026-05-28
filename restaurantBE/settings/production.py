"""
Setting for production deployment
"""

import os
from .common import *
from urllib.parse import urlparse, parse_qsl

DEBUG = os.getenv("ENV", default="dev") == "dev"

SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"
)

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ".onrender.com,localhost,127.0.0.1").split(
    ","
)
HOST = os.getenv("HOST", "http://localhost:8000/")

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


# Replace the DATABASES section of your settings.py with this
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

# CORS config
_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").strip()
if _cors_origins == "*":
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
else:
    CORS_ALLOWED_ORIGINS = [
        origin.strip() for origin in _cors_origins.split(",") if origin.strip()
    ]
