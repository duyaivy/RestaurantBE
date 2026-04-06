"""Synchronous emit helpers for Django signal handlers."""

from asgiref.sync import async_to_sync

from .server import sio


def emit_new_order(order_data: dict):
    """Call from signal when a new Order is created."""
    async_to_sync(sio.emit)(
        "order_created",
        order_data,
        room="staff_notifications",
    )
    
    table_number = order_data.get("table_number")
    if table_number is not None:
        async_to_sync(sio.emit)(
            "order_created",
            order_data,
            room=f"table_{table_number}",
        )


def emit_order_updated(table_number: int, order_data: dict):
    """Call from signal when an Order is updated."""
    async_to_sync(sio.emit)(
        "order_status_updated",
        order_data,
        room=f"table_{table_number}",
    )
    
    async_to_sync(sio.emit)(
        "order_status_updated",
        order_data,
        room="staff_notifications",
    )
