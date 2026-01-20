"""
Setting for production deployment
"""

from .common import *

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME", "restaurant"),
        "USER": os.getenv("DB_USERNAME", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# CORS config
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(
    ","
)
