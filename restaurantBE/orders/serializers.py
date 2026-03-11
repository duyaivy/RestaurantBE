from email.mime import image

from rest_framework.exceptions import ValidationError
from restaurantBE.constants import TableStatus
from restaurantBE.constants import OrderStatus
from restaurantBE.tables.models import Table
from restaurantBE.constants.common import Constant
from restaurantBE.constants import DishStatus
from restaurantBE.dishes.models import Dish
from rest_framework import serializers
from restaurantBE.orders.models import Order, OrderItem
from django.utils.translation import gettext_lazy as _


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
