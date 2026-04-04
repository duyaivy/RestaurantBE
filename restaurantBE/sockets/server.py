"""Socket.IO server setup backed by Redis pub/sub."""

import socketio
from django.conf import settings

REDIS_URL = settings.REDIS_URL

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # tighten this in production
    client_manager=socketio.AsyncRedisManager(url=REDIS_URL),
)

socket_app = socketio.ASGIApp(sio, socketio_path="socket.io")
