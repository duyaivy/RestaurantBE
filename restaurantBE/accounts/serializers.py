import re
from rest_framework import serializers

from restaurantBE.accounts.models import Account


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255,
        min_length=6,
        error_messages={
            "invalid": "Địa chỉ email không hợp lệ.",
            "max_length": "Địa chỉ email không được vượt quá 255 ký tự.",
            "min_length": "Địa chỉ email phải có ít nhất 6 ký tự.",
            "blank": "Địa chỉ email không được để trống.",
        },
    )
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            "min_length": "Mật khẩu phải có ít nhất 8 ký tự.",
            "max_length": "Mật khẩu không được vượt quá 255 ký tự.",
            "blank": "Mật khẩu không được để trống.",
        },
    )

    class Meta:
        model = Account  # Replace with your User model
        fields = ("id", "email", "name", "password", "role", "avatar", "owner_id")
        extra_kwargs = {
            "role": {"default": "EMPLOYEE"},
            "avatar": {"required": False, "allow_null": True, "allow_blank": True},
            "owner_id": {"required": False, "allow_null": True},
        }

    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã tồn tại.")
        return value.lower()

    def validate_password(self, value):
        pattern = r"^(?=.*[a-z])(?=.*[^A-Za-z0-9]).{8,}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ cái và số."
            )
        return value

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name", "email", "avatar", "role", "create_at", "update_at")
        read_only_fields = ("id", "create_at", "update_at")
