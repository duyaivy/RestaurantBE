"""Socket.IO event handlers."""

import logging
from urllib.parse import parse_qs

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .server import sio

logger = logging.getLogger(__name__)


@sio.event
async def connect(sid, environ, auth):
    """Authenticate and join a room based on JWT role."""
    try:
        token = auth.get("token") if auth and isinstance(auth, dict) else None
        if not token:
            token = parse_qs(environ.get("QUERY_STRING", "")).get("token", [None])[0]

        payload = AccessToken(token).payload
        role = payload["role"]

        if role == "staff":
            room = "staff_notifications"
        elif role == "guest":
            room = f"table_{payload['table_number']}"
        else:
            raise ConnectionRefusedError("unauthorized")

        await sio.enter_room(sid, room)
        await sio.save_session(sid, {"room": room, "role": role})
        logger.info("SIO connected sid=%s role=%s room=%s", sid, role, room)
    except (InvalidToken, TokenError, KeyError, TypeError):
        raise ConnectionRefusedError("invalid token")


@sio.event
async def disconnect(sid):
    """Clean up room membership on disconnect."""
    try:
        session = await sio.get_session(sid)
        if session and "room" in session:
            await sio.leave_room(sid, session["room"])
    except KeyError:
        # Session may not exist for rejected/partial connections.
        pass
