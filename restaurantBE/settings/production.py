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


database_url = os.getenv("DATABASE_URL")
if database_url:
    tmpPostgres = urlparse(database_url)
    db_name = tmpPostgres.path.replace("/", "") if tmpPostgres.path else os.getenv("DB_NAME", "restaurant")
    db_user = tmpPostgres.username or os.getenv("DB_USERNAME", "postgres")
    db_password = tmpPostgres.password or os.getenv("DB_PASSWORD", "postgres")
    db_host = tmpPostgres.hostname or os.getenv("DB_HOST", "localhost")
    db_port = tmpPostgres.port or int(os.getenv("DB_PORT", 5432))
    db_options = dict(parse_qsl(tmpPostgres.query)) if tmpPostgres.query else {}
else:
    db_name = os.getenv("DB_NAME", "restaurant")
    db_user = os.getenv("DB_USERNAME", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_options = {}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_name,
        "USER": db_user,
        "PASSWORD": db_password,
        "HOST": db_host,
        "PORT": db_port,
        "OPTIONS": db_options,
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
