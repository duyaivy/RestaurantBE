from django_filters import FilterSet, NumberFilter

from restaurantBE.dishes.models import Dish


class DishFilter(FilterSet):
    category_id = NumberFilter(field_name="category_id", lookup_expr="exact")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Dish
        fields = ["category_id", "status"]
