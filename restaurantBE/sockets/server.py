"""Socket.IO server setup backed by Redis pub/sub."""

import os

import socketio


def _get_redis_url() -> str:
    """Prefer Django settings, fallback to environment/default for local runs."""
    try:
        from django.conf import settings

        return getattr(settings, "REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    except Exception:
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")


REDIS_URL = _get_redis_url()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # tighten this in production
    client_manager=socketio.AsyncRedisManager(url=REDIS_URL),
)

socket_app = socketio.ASGIApp(sio, socketio_path="socket.io")
