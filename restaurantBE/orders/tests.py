from django.test import SimpleTestCase

from restaurantBE.constants import OrderItemStatus
from restaurantBE.orders.serializers import OrderItemUpdateSerializer


class OrderItemUpdateSerializerTests(SimpleTestCase):
    def test_accepts_item_status_field(self):
        serializer = OrderItemUpdateSerializer(
            data={
                "order_item_id": 47,
                "quantity": 3,
                "note": "",
                "item_status": OrderItemStatus.COOKING,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["item_status"], OrderItemStatus.COOKING)
        self.assertNotIn("status", serializer.validated_data)

    def test_normalizes_status_alias_to_item_status(self):
        serializer = OrderItemUpdateSerializer(
            data={
                "order_item_id": 47,
                "status": OrderItemStatus.SERVED,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["item_status"], OrderItemStatus.SERVED)
        self.assertNotIn("status", serializer.validated_data)

    def test_rejects_conflicting_item_status_values(self):
        serializer = OrderItemUpdateSerializer(
            data={
                "order_item_id": 47,
                "item_status": OrderItemStatus.COOKING,
                "status": OrderItemStatus.SERVED,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
