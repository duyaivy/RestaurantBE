from rest_framework.exceptions import ValidationError
from restaurantBE.accounts.models import Account
from restaurantBE.constants import TableStatus, OrderStatus, ORDER_STATUS_TRANSITIONS
from restaurantBE.constants.choices import Role
from restaurantBE.tables.models import Table
from restaurantBE.constants.common import Constant
from restaurantBE.constants import DishStatus
from restaurantBE.dishes.models import Dish
from rest_framework import serializers
from restaurantBE.orders.models import Order, OrderItem
from django.utils.translation import gettext_lazy as _
from django.db import transaction


class OrderSerializer(serializers.ModelSerializer):
    """Basic Order serializer"""

    class Meta:
        model = Order
        fields = [
            "id",
            "guest_id",
            "table_number",
            "order_handler_id",
            "status",
            "payment_method",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    """Basic OrderItem serializer"""

    name = serializers.JSONField(source="dish_snapshot_id.name", read_only=True)
    price = serializers.DecimalField(
        source="dish_snapshot_id.price", max_digits=10, decimal_places=2, read_only=True
    )
    image = serializers.CharField(
        source="dish_snapshot_id.image", max_length=255, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order_id",
            "name",
            "price",
            "image",
            "quantity",
            "note",
            "item_status",
            "total_amount",
        ]
        read_only_fields = ["id", "order_id"]


class OrderItemCreateSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    note = serializers.CharField(allow_blank=True, required=False)


class OrderCreateSerializer(serializers.Serializer):
    """Basic Order serializer"""

    table_number_id = serializers.IntegerField(required=True)
    items = OrderItemCreateSerializer(many=True, required=True)

    def validate_table_number_id(self, value):
        if not Table.objects.filter(number=value).exists():
            raise serializers.ValidationError(_("table_not_found"))
        if Table.objects.filter(number=value).first().status != TableStatus.AVAILABLE:
            raise ValidationError(_("table_not_available"))
        return value

    def validate_items(self, value):
        if not value:
            raise ValidationError(_("order_items_required"))
        return value


class OrderUpdateStatusSerializer(serializers.Serializer):
    """Serializer for updating order status only"""

    status = serializers.ChoiceField(choices=OrderStatus.choices)

    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.context.get("instance")
        if not instance:
            return value

        current_status = instance.status

        # Validate transition
        if value not in ORDER_STATUS_TRANSITIONS.get(current_status, []):
            raise ValidationError(_("invalid_status_transition"))

        return value


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order - chỉ cho phép update các field cụ thể"""

    order_handler_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            "status",
            "payment_method",
            "table_number",
            "order_handler_id",
        ]

    def validate_table_number(self, value):
        """Validate table khi thay đổi bàn"""
        if not Table.objects.filter(number=value.number).exists():
            raise serializers.ValidationError(_("table_not_found"))

        table = Table.objects.get(number=value.number)

        if self.instance and self.instance.table_number.number != value.number:
            if table.status != TableStatus.AVAILABLE:
                raise ValidationError(_("table_not_available"))

        return value

    def validate_order_handler_id(self, value):
        """Validate order handler (employee or admin)"""
        if value is None:
            return value

        try:
            user = Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise ValidationError(_("user_not_found"))

        if user.role not in [Role.EMPLOYEE, Role.ADMIN]:
            raise ValidationError(_("user_must_be_employee_or_admin"))

        # Trả về Account instance để Django có thể gán vào ForeignKey
        return user

    def validate_status(self, value):
        """Validate status transitions"""
        if not self.instance:
            return value

        current_status = self.instance.status

        if value == OrderStatus.CANCELLED:
            raise ValidationError(_("cannot_update_to_canceled_status"))

        if value not in ORDER_STATUS_TRANSITIONS.get(current_status, []):
            raise ValidationError(_("invalid_status_transition"))

        return value

    def validate(self, data):
        """Validate toàn bộ data"""
        if self.instance and self.instance.status in [
            OrderStatus.CANCELLED,
            OrderStatus.COMPLETED,
        ]:
            raise ValidationError(_("cannot_update_cancelled_or_completed_order"))

        return data

    def update(self, instance, validated_data):
        """Override update để xử lý logic đổi bàn"""
        old_table = instance.table_number
        new_table = validated_data.get("table_number")

        if new_table and old_table.number != new_table.number:
            with transaction.atomic():
                # Bàn cũ trở về available
                old_table.status = TableStatus.AVAILABLE
                old_table.save()

                # Bàn mới thành reserved
                new_table.status = TableStatus.RESERVED
                new_table.save()

        return super().update(instance, validated_data)


class OrderItemActionSerializer(serializers.Serializer):
    """Serializer cho việc thêm dish vào order"""

    dish_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)
    note = serializers.CharField(allow_blank=True, required=False, default="")

    def validate_dish_id(self, value):
        try:
            dish = Dish.objects.get(id=value)
            if dish.status != DishStatus.AVAILABLE:
                raise ValidationError(_("dish_not_available"))
        except Dish.DoesNotExist:
            raise ValidationError(_("dish_not_found"))
        return value


class OrderItemUpdateSerializer(serializers.Serializer):

    order_item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)
    note = serializers.CharField(allow_blank=True, required=False)


class OrderItemsUpdateSerializer(serializers.Serializer):
    """Serializer cho việc update order items (add/update/cancel)"""

    add_items = OrderItemActionSerializer(many=True, required=False, default=list)
    update_items = OrderItemUpdateSerializer(many=True, required=False, default=list)
    cancel_item_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )

    def validate_cancel_item_ids(self, value):
        """Validate các order item IDs tồn tại"""
        if not value:
            return value

        # Kiểm tra context có order_id không
        order_id = self.context.get("order_id")
        if not order_id:
            raise ValidationError(_("order_id_required"))

        # Kiểm tra tất cả items thuộc về order này
        existing_items = OrderItem.objects.filter(
            id__in=value, order_id=order_id
        ).values_list("id", flat=True)

        if len(existing_items) != len(value):
            invalid_ids = set(value) - set(existing_items)
            raise ValidationError(_(f"order_items_not_found: {invalid_ids}"))

        return value

    def validate_update_items(self, value):
        """Validate các order item IDs trong update_items tồn tại"""
        if not value:
            return value

        order_id = self.context.get("order_id")
        if not order_id:
            raise ValidationError(_("order_id_required"))

        order_item_ids = [item["order_item_id"] for item in value]
        existing_items = OrderItem.objects.filter(
            id__in=order_item_ids, order_id=order_id
        ).values_list("id", flat=True)

        if len(existing_items) != len(order_item_ids):
            invalid_ids = set(order_item_ids) - set(existing_items)
            raise ValidationError(_(f"order_items_not_found: {invalid_ids}"))

        return value

    def validate_add_items(self, value):
        if not value:
            return value

        order_id = self.context.get("order_id")
        if not order_id:
            return value

        # Lấy các dish_id đang muốn add
        dish_ids_to_add = [item["dish_id"] for item in value]

        # Lấy các dish_id đã có trong order (chưa bị cancel)
        from restaurantBE.constants import OrderItemStatus

        existing_dish_ids = (
            OrderItem.objects.filter(order_id=order_id)
            .exclude(item_status=OrderItemStatus.CANCELLED)
            .values_list("dish_snapshot_id__dish_id", flat=True)
        )

        # Check trùng
        duplicate_dish_ids = set(dish_ids_to_add) & set(existing_dish_ids)

        if duplicate_dish_ids:
            raise ValidationError(_(f"duplicate_dishes_in_order"))

        return value

    def validate(self, data):

        if (
            not data.get("add_items")
            and not data.get("cancel_item_ids")
            and not data.get("update_items")
        ):
            raise ValidationError(_("at_least_one_action_required"))

        return data
