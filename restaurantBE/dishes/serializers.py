from rest_framework import serializers
from restaurantBE.categories.models import Category, CategoryBriefSerializer
from restaurantBE.dishes.models import Dish
from django.utils.translation import gettext_lazy as _


class DishSerializer(serializers.ModelSerializer):
    category = CategoryBriefSerializer(source="category_id", read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Dish
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(_("name_must_be_json"))
        if not value:
            raise serializers.ValidationError(_("name_required"))
        return value

    def validate_description(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(_("description_must_be_json"))
        if not value:
            raise serializers.ValidationError(_("description_required"))
        return value

    def validate_price(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError(_("price_invalid"))
        return value
