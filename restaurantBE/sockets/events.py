"""Socket.IO event handlers."""

import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from restaurantBE.constants.choices import Role
from restaurantBE.guests.models import Guest
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .server import sio

logger = logging.getLogger(__name__)


def _table_room(table_number: int) -> str:
    return f"table_{table_number}"


async def _resolve_guest_table_number(payload: dict) -> int:
    table_number = payload.get("table_number")
    if table_number is not None:
        return int(table_number)

    guest_id = payload.get("guest_id")
    if guest_id is None:
        raise KeyError("guest_id")

    guest = await sync_to_async(Guest.objects.only("tableNumber_id").get)(id=guest_id)
    return int(guest.tableNumber_id)


@sio.event
async def connect(sid, environ, auth):
    """Authenticate and join a room based on JWT role."""
    try:
        token = auth.get("token") if auth and isinstance(auth, dict) else None
        if not token:
            token = parse_qs(environ.get("QUERY_STRING", "")).get("token", [None])[0]

        payload = AccessToken(token).payload
        role = str(payload["role"]).upper()
        actor_id = payload.get("user_id") or payload.get("guest_id")
        session_data = {"role": role, "actor_id": actor_id}

        if role in {Role.ADMIN, Role.EMPLOYEE}:
            room = "staff_notifications"
            session_data["room"] = room
        elif role == Role.GUEST:
            table_number = await _resolve_guest_table_number(payload)
            room = _table_room(table_number)
            session_data["room"] = room
            session_data["table_number"] = table_number
        else:
            raise ConnectionRefusedError("unauthorized")

        await sio.enter_room(sid, room)
        await sio.save_session(sid, session_data)
        logger.info("SIO connected sid=%s role=%s room=%s", sid, role, room)
    except (InvalidToken, TokenError, KeyError, TypeError):
        raise ConnectionRefusedError("invalid token")


@sio.event
async def disconnect(sid):
    """Clean up room membership on disconnect."""
    logger.info("SIO disconnect sid=%s", sid)
    try:
        session = await sio.get_session(sid)
        if session and "room" in session:
            await sio.leave_room(sid, session["room"])
    except KeyError:
        # Session may not exist for rejected/partial connections.
        pass


@sio.event
async def chat_send(sid, data):
    """Send chat message between staff and guest."""
    logger.info("SIO chat_send sid=%s data=%s", sid, data)
    session = await sio.get_session(sid)
    payload = data if isinstance(data, dict) else {}
    message = str(payload.get("message", "")).strip()

    if not message:
        await sio.emit("chat_error", {"message": "message_required"}, to=sid)
        return {"ok": False, "message": "message_required"}

    role = session.get("role")
    
    # Identify target table
    if role in {Role.ADMIN, Role.EMPLOYEE}:
        try:
            table_number = int(payload.get("table_number"))
        except (TypeError, ValueError):
            await sio.emit("chat_error", {"message": "table_number_required"}, to=sid)
            return {"ok": False, "message": "table_number_required"}
    else:
        table_number = session.get("table_number")
        if not table_number:
            await sio.emit("chat_error", {"message": "guest_has_no_table"}, to=sid)
            return {"ok": False, "message": "guest_has_no_table"}

    chat_payload = {
        "message": message,
        "sender_role": role,
        "sender_id": session.get("actor_id"),
        "table_number": table_number,
    }

    # Broadcast to both table room and staff room so everyone sees it
    table_room = _table_room(table_number)
    staff_room = "staff_notifications"

    await sio.emit("chat_message", chat_payload, room=table_room)
    await sio.emit("chat_message", chat_payload, room=staff_room)
    
    return {"ok": True}


@sio.on("*")
async def catch_all(event, sid, *args):
    """Catch all other events for debugging."""
    logger.info("SIO catch_all sid=%s event=%s data=%s", sid, event, args)

