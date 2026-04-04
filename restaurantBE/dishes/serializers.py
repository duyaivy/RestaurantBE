from rest_framework import serializers
from restaurantBE.categories.models import Category, CategoryBriefSerializer
from restaurantBE.dishes.models import Dish
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from restaurantBE.utils.translation import normalize_localized_field


SOURCE_LANGUAGE = "vi"
SUPPORTED_LANGS = tuple(code for code, _ in settings.LANGUAGES)


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

    def _normalize_localized_field(self, value, field_key):
        try:
            return normalize_localized_field(
                value,
                field_key=field_key,
                source_language=SOURCE_LANGUAGE,
                target_languages=SUPPORTED_LANGS,
            )
        except serializers.ValidationError as exc:
            raise serializers.ValidationError(_(str(exc.detail[0])))

    def validate_name(self, value):
        return self._normalize_localized_field(value, "name")

    def validate_description(self, value):
        return self._normalize_localized_field(value, "description")

    def validate_price(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError(_("price_invalid"))
        return value
