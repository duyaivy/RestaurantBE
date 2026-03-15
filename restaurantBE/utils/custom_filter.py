from django_filters import FilterSet, NumberFilter, CharFilter,  DateTimeFilter

from restaurantBE.dishes.models import Dish
from restaurantBE.orders.models import Order


class DishFilter(FilterSet):
    category_id = NumberFilter(field_name="category_id", lookup_expr="exact")
    category = NumberFilter(field_name="category_id", lookup_expr="exact")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Dish
        fields = ["category_id", "category", "status"]


class OrderFilter(FilterSet):
    guest_id = NumberFilter(field_name="guest_id", lookup_expr="exact")
    order_handler_id = NumberFilter(field_name="order_handler_id", lookup_expr="exact")
    status = CharFilter(field_name="status", lookup_expr="exact")
    from_date = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    to_date = DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["guest_id", "order_handler_id", "status"]
