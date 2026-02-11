from os import error, write
import re
from django.utils.translation import gettext as _
from restaurantBE.accounts.models import Account
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework import serializers
from django.utils.translation import gettext as _
from restaurantBE.accounts.serializers.accounts import AccountSerializer


from restaurantBE.constants import Role


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255,
        min_length=6,
        error_messages={
            "invalid": _("email_invalid"),
            "max_length": _("email_max_length"),
            "min_length": _("email_min_length"),
            "blank": _("email_blank"),
        },
    )
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        error_messages={
            "min_length": _("password_min_length"),
            "max_length": _("password_max_length"),
            "blank": _("password_blank"),
        },
    )

    class Meta:
        model = Account  # Replace with your User model
        fields = ("id", "email", "name", "password", "role", "avatar", "owner_id")
        extra_kwargs = {
            "role": {"default": Role.EMPLOYEE},
            "avatar": {"required": False, "allow_null": True, "allow_blank": True},
            "owner_id": {"required": False, "allow_null": True},
        }

    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("email_exists"))
        return value.lower()

    def validate_password(self, value):
        pattern = r"^(?=.*[a-z])(?=.*[^A-Za-z0-9]).{8,}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(_("password_invalid"))
        return value

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user_id"] = user.id
        token["role"] = user.role
        token["user_type"] = "account"  # Distinguish from guest tokens

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        return {
            "accessToken": data["access"],
            "refreshToken": data["refresh"],
            "account": AccountSerializer(self.user).data,
        }


class RefreshTokenSerializer(TokenRefreshSerializer):
    refresh = None
    refreshToken = serializers.CharField(
        write_only=True,
        error_messages={
            "blank": _("refresh_token_blank"),
            "required": _("refresh_token_required"),
        },
    )

    def validate(self, attrs):
        # lay token, validate
        attrs["refresh"] = attrs.pop("refreshToken")
        data = super().validate(attrs)

        return {
            "accessToken": data["access"],
            "refreshToken": data.get("refresh", None),
        }
