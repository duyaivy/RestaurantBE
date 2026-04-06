"""
Django signals for real-time order notifications via Socket.IO.

Fires on Order post_save:
  - created → emit "order_created" to staff_notifications room
  - updated → emit "order_status_updated" to table_{N} room

NOTE: This module must NOT be imported at module level from apps other
than orders.apps.OrdersConfig.ready(). Importing it elsewhere can
trigger Django app-loading before all apps are ready.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from restaurantBE.orders.models import Order
from restaurantBE.orders.serializers import OrderSocketSerializer
from restaurantBE.sockets.utils import emit_new_order, emit_order_updated

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def on_order_saved(sender, instance, created, **kwargs):
    """
    Emit Socket.IO events when an Order is created or updated.

    Emits to staff room on create and to the guest table room on update.
    """
    try:
        serializer = OrderSocketSerializer(instance)
        data = serializer.data

        if created:
            emit_new_order(data)
        else:
            emit_order_updated(instance.table_number_id, data)

    except Exception as exc:
        # Never let a socket emit failure break the request cycle
        logger.error("Signal on_order_saved failed: %s", exc, exc_info=True)
