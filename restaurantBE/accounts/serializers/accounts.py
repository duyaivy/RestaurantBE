from rest_framework import serializers
from restaurantBE.accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name", "email", "avatar", "role", "create_at", "update_at")
        read_only_fields = ("id", "role", "create_at", "update_at")
