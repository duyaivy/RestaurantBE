"""
ASGI config for restaurantBE project.

Routes:
  /socket.io/*  → python-socketio (WebSocket + long-polling)
  everything    → Django (REST API)

Run with:
  uvicorn restaurantBE.asgi:application --host 0.0.0.0 --port 8000
"""

import os
from dotenv import load_dotenv
from socketio import ASGIApp

# Load environment variables from .env file
load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurantBE.settings.production")

# Django ASGI app must be created BEFORE importing Socket.IO modules
# to ensure Django's app registry is fully populated.
from django.core.asgi import get_asgi_application
django_app = get_asgi_application()

# Import after Django is ready
from restaurantBE.sockets.server import sio

# Register Socket.IO event handlers (side-effect import)
import restaurantBE.sockets.events  # noqa: F401

# Mount Socket.IO on /socket.io/, fall through to Django for everything else
application = ASGIApp(
    sio,
    other_asgi_app=django_app,
    socketio_path="socket.io",
)
