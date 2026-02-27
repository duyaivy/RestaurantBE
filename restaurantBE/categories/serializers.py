from rest_framework import serializers
from restaurantBE.categories.models import Category
from django.utils.translation import gettext_lazy as _

SUPPORTED_LANGS = ("vi", "en")


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    """

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        """
        Validate multilingual JSON name: {"vi": "...", "en": "..."}
        - require vi
        - en optional (if provided must be non-empty)
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError(_("not_an_object"))

        # block unsupported keys
        extra_keys = set(value.keys()) - set(SUPPORTED_LANGS)
        if extra_keys:
            raise serializers.ValidationError(
                _("unsupported_language_keys_in_name", extra_keys=sorted(extra_keys))
            )

        vi = value.get("vi")
        en = value.get("en")

        if not isinstance(vi, str) or not vi.strip():
            raise serializers.ValidationError(_("cannot_be_empty"))

        if en is not None and (not isinstance(en, str) or not en.strip()):
            raise serializers.ValidationError(
                _("name_en_must_be_non_empty_string_if_provided")
            )

        return value

    def validate_description(self, value):
        """
        Validate multilingual JSON description: {"vi": "...", "en": "..."} or null
        """
        if value is None:
            return value

        if not isinstance(value, dict):
            raise serializers.ValidationError(_("description_must_be_object"))

        extra_keys = set(value.keys()) - set(SUPPORTED_LANGS)
        if extra_keys:
            raise serializers.ValidationError(
                _(
                    "unsupported_language_keys_in_description",
                    extra_keys=sorted(extra_keys),
                )
            )

        vi = value.get("vi")
        en = value.get("en")

        # description optional, but if provided must be string
        if vi is not None and not isinstance(vi, str):
            raise serializers.ValidationError(_("description_must_be_string"))

        if en is not None and not isinstance(en, str):
            raise serializers.ValidationError(_("description_must_be_string"))

        return value
