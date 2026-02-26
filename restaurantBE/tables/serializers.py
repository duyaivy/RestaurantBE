from restaurantBE.constants.common import Constant
from rest_framework import serializers
from restaurantBE.tables.models import Table
from django.utils.translation import gettext_lazy as _
from restaurantBE.utils.random import RandomUtils

class TableSerializer(serializers.ModelSerializer):
    changeToken = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Table
        fields = "__all__"
        read_only_fields = ["token"]
        extra_kwargs = {
            'number': {'required': False}  
        }

    def validate_number(self, value):
        instance = self.instance
        if instance is None:
            if Table.objects.filter(number=value).exists():
                raise serializers.ValidationError(_("table_already_exists"))
        else:
            if instance.number != value:
                if Table.objects.filter(number=value).exists():
                    raise serializers.ValidationError(_("table_already_exists"))

        return value

    def validate_capacity(self, value):
        if value is None or value < Constant.MIN_CAPACITY or value > Constant.MAX_CAPACITY:
            raise serializers.ValidationError(_("capacity_invalid"))
        return value

    def create(self, validated_data):
        validated_data.pop("changeToken", None)
        data = super().create(validated_data)
        data.token = RandomUtils.generateToken()
        data.save()
        return data

    def update(self, instance, validated_data):
        change_token = validated_data.pop("changeToken", False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if change_token:
            instance.token = RandomUtils.generateToken()

        instance.save()
        return instance