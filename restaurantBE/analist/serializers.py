from datetime import datetime
from calendar import monthrange

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AnalistDateRangeSerializer(serializers.Serializer):
    from_datetime = serializers.DateTimeField(required=False)
    to = serializers.DateTimeField(required=False)

    def to_internal_value(self, data):
        payload = data.copy()

        # Accept query key `from` while keeping Python-safe field naming.
        if "from" in payload and "from_datetime" not in payload:
            payload["from_datetime"] = payload.get("from")

        return super().to_internal_value(payload)

    def validate(self, attrs):
        default_to = timezone.now()
        to_datetime = attrs.get("to") or default_to
        from_datetime = attrs.get("from_datetime") or self._subtract_one_month(
            to_datetime
        )

        if from_datetime > to_datetime:
            raise ValidationError({"from": _("from_must_be_before_or_equal_to_to")})

        attrs["from_datetime"] = from_datetime
        attrs["from"] = from_datetime
        attrs["to"] = to_datetime
        return attrs

    @staticmethod
    def _subtract_one_month(value: datetime) -> datetime:
        year = value.year
        month = value.month - 1

        if month == 0:
            month = 12
            year -= 1

        last_day_of_month = monthrange(year, month)[1]
        day = min(value.day, last_day_of_month)

        return value.replace(year=year, month=month, day=day)
