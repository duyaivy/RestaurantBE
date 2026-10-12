"""
Order Service
Single Responsibility: Chứa toàn bộ business logic liên quan đến Order.
View chỉ gọi service, không tự xử lý DB hay business logic.
"""

from __future__ import annotations

from typing import List, Optional

from django.db import models, transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from restaurantBE.constants import (
    OrderItemStatus,
    OrderStatus,
    PaymentMethod,
    TableStatus,
)
from restaurantBE.dishes.models import Dish, DishSnapshot
from restaurantBE.orders.models import Order, OrderItem
from restaurantBE.tables.models import Table


class OrderService:
    """
    Single Responsibility: chứa toàn bộ business logic liên quan đến Order.
    View chỉ gọi service, không tự xử lý DB hay business logic.
    """

    @staticmethod
    def create_order(
        guest,  # Guest instance (request.user)
        table_id: int,  # Table number (int)
        items: list[dict],  # [{"dish_id": int, "quantity": int, "note": str}]
        order_handler=None,  # Account instance hoặc None
    ) -> Order:
        """
        Tạo order hoàn chỉnh trong một transaction:
        1. Lock table (select_for_update)
        2. Set table.status = RESERVED
        3. Validate tất cả dish_id tồn tại
        4. Tạo DishSnapshot cho từng món
        5. Tạo OrderItem
        6. Tính và lưu total_amount
        Raise: ValidationError nếu dish không tồn tại
        """
        with transaction.atomic():
            table = Table.objects.select_for_update().get(number=table_id)
            table.status = TableStatus.RESERVED
            table.save()

            dish_ids = [item["dish_id"] for item in items]
            dishes = Dish.objects.filter(id__in=dish_ids)
            if dishes.count() != len(dish_ids):
                raise ValidationError(_("dish_not_found"))

            order = Order.objects.create(
                guest_id=guest,
                table_number_id=table_id,
                order_handler_id=order_handler,
                payment_method=PaymentMethod.CASH,
                total_amount=0,
            )

            total_amount = 0
            for item in items:
                dish = dishes.get(id=item["dish_id"])
                dish_snapshot = DishSnapshot.objects.create(
                    dish_id=dish,
                    name=dish.name,
                    price=dish.price,
                    description=dish.description,
                    image=dish.image,
                )
                amount = dish_snapshot.price * item["quantity"]
                OrderItem.objects.create(
                    order_id=order,
                    dish_snapshot_id=dish_snapshot,
                    quantity=item["quantity"],
                    note=item.get("note", "") or "",
                    item_status=OrderItemStatus.ORDERED,
                    total_amount=amount,
                )
                total_amount += amount

            order.total_amount = total_amount
            order.save()
            return order

    @staticmethod
    def update_order_status(order: Order, new_status: str) -> Order:
        """
        Cập nhật status của order.
        Nếu new_status == COMPLETED: set table.status = AVAILABLE (CHỈ MỘT LẦN).
        """
        with transaction.atomic():
            order.status = new_status
            order.save()

            if order.status == OrderStatus.COMPLETED:
                table = Table.objects.filter(number=order.table_number_id).first()
                if table:
                    table.status = TableStatus.AVAILABLE
                    table.save()

            return order

    @staticmethod
    def add_items_to_order(order: Order, items: list[dict]) -> list[OrderItem]:
        """Thêm các item mới vào order đang tồn tại."""
        if not items:
            return []

        dish_ids = [item["dish_id"] for item in items]
        dishes = Dish.objects.filter(id__in=dish_ids)
        dishes_dict = {dish.id: dish for dish in dishes}

        added_items = []
        for item_data in items:
            dish = dishes_dict.get(item_data["dish_id"])
            if not dish:
                continue

            dish_snapshot = DishSnapshot.objects.create(
                dish_id=dish,
                name=dish.name,
                price=dish.price,
                description=dish.description,
                image=dish.image,
            )
            quantity = item_data["quantity"]
            total_amount = dish_snapshot.price * quantity

            order_item = OrderItem.objects.create(
                order_id=order,
                dish_snapshot_id=dish_snapshot,
                quantity=quantity,
                note=item_data.get("note", "") or "",
                item_status=OrderItemStatus.ORDERED,
                total_amount=total_amount,
            )
            added_items.append(order_item)

        return added_items

    @staticmethod
    def update_order_items(order: Order, items: list[dict]) -> list[OrderItem]:
        """Cập nhật quantity/note/status của các item hiện có."""
        updated_items = []
        for item_data in items:
            order_item = OrderItem.objects.select_for_update().get(
                id=item_data["order_item_id"], order_id=order
            )

            if "quantity" in item_data:
                order_item.quantity = item_data["quantity"]
                order_item.total_amount = (
                    order_item.dish_snapshot_id.price * order_item.quantity
                )

            if "note" in item_data:
                order_item.note = item_data["note"]

            if "item_status" in item_data:
                order_item.item_status = item_data["item_status"]

            order_item.save()
            updated_items.append(order_item)

        return updated_items

    @staticmethod
    def cancel_order_items(order: Order, item_ids: list[int]) -> int:
        """Cancel các item theo id, trả về số lượng item đã cancel."""
        if not item_ids:
            return 0
        cancelled_count = OrderItem.objects.filter(
            id__in=item_ids, order_id=order
        ).update(item_status=OrderItemStatus.CANCELLED)
        return cancelled_count

    @staticmethod
    def recalculate_total(order: Order) -> Order:
        """Tính lại total_amount từ các active items, lưu và return order."""
        total_amount = (
            OrderItem.objects.filter(order_id=order)
            .exclude(item_status=OrderItemStatus.CANCELLED)
            .aggregate(total=models.Sum("total_amount"))["total"]
            or 0
        )
        order.total_amount = total_amount
        order.save()
        return order
