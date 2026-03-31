from restaurantBE.constants.choices import OrderItemStatus
from restaurantBE.dishes.models import DishSnapshot
from restaurantBE.tables.models import Table
from restaurantBE.accounts.models import Account
from restaurantBE.constants.choices import OrderStatus
from restaurantBE.constants.choices import PaymentMethod
from restaurantBE.guests.models import Guest
from django.db import models


class Order(models.Model):
    guest_id = models.ForeignKey(
        Guest, on_delete=models.PROTECT
    )  # khong cho xoa cha neu con order
    table_number = models.ForeignKey(Table, on_delete=models.PROTECT)
    order_handler_id = models.ForeignKey(Account, on_delete=models.PROTECT, null=True)
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["created_at"], name="idx_order_created_at"),
            models.Index(
                fields=["status", "created_at"],
                name="idx_order_status_created_at",
            ),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish_snapshot_id = models.ForeignKey(DishSnapshot, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    note = models.CharField(max_length=255, blank=True, null=True)
    item_status = models.CharField(
        max_length=20, choices=OrderItemStatus.choices, default=OrderItemStatus.ORDERED
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order_items"
        indexes = [
            models.Index(fields=["order_id"], name="idx_order_item_order_id"),
            models.Index(
                fields=["dish_snapshot_id"], name="idx_order_item_snapshot_id"
            ),
            models.Index(fields=["created_at"], name="idx_order_item_created_at"),
            models.Index(fields=["item_status"], name="idx_order_item_status"),
            models.Index(
                fields=["item_status", "order_id"],
                name="idx_order_item_status_order",
            ),
        ]

    def __str__(self):
        return f"OrderItem {self.id} - {self.dish_snapshot_id}"
