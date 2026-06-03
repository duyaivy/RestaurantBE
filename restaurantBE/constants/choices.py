from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    ADMIN = "ADMIN", _("admin")
    EMPLOYEE = "EMPLOYEE", _("employee")
    GUEST = "GUEST", _("guest")


class TableStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", _("available")
    RESERVED = "RESERVED", _("reserved")
    HIDDEN = "HIDDEN", _("hidden")


class DishStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", _("available")
    UNAVAILABLE = "UNAVAILABLE", _("unavailable")
    HIDDEN = "HIDDEN", _("hidden")


class PaymentMethod(models.TextChoices):
    CASH = "CASH", _("cash")
    QR_CODE = "QR_CODE", _("qr_code")


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", _("pending")
    PREPARING = "PREPARING", _("preparing")
    SERVED = "SERVED", _("served")
    CANCELLED = "CANCELLED", _("cancelled")
    COMPLETED = "COMPLETED", _("completed")


class OrderItemStatus(models.TextChoices):
    ORDERED = "ORDERED", _("ordered")
    COOKING = "COOKING", _("cooking")
    SERVED = "SERVED", _("served")
    CANCELLED = "CANCELLED", _("cancelled")


ALL_ORDER_STATUSES = [
    OrderStatus.PENDING,
    OrderStatus.PREPARING,
    OrderStatus.SERVED,
    OrderStatus.CANCELLED,
    OrderStatus.COMPLETED,
]

# Valid order status transitions
ORDER_STATUS_TRANSITIONS = {
    OrderStatus.PENDING: ALL_ORDER_STATUSES,
    OrderStatus.PREPARING: ALL_ORDER_STATUSES,
    OrderStatus.SERVED: ALL_ORDER_STATUSES,
    OrderStatus.COMPLETED: ALL_ORDER_STATUSES,
    OrderStatus.CANCELLED: ALL_ORDER_STATUSES,
}
