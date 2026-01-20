import re
from rest_framework import serializers

from restaurantBE.roles.serializers import RoleSerializer
from restaurantBE.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50, min_length=6)
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "email", "role", "password")

    def validate_email(self, value):
        if User.objects.filter(email__icontains=value).exists():
            raise serializers.ValidationError({"email": "email is already taken"})

        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        result = re.match(pattern, value)

        if result is None:
            raise serializers.ValidationError({"email": "email is invalid format"})

        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError({"password": "password is required"})
        # Regular expression to check for at least 8 characters, one number, one letter, and one special character
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        result = re.match(pattern, value)

        if result is None:
            raise serializers.ValidationError(
                {
                    "password": "Password must be at least 8 characters long, include at least one number, one letter, and one special character."
                }
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "role",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"password": {"write_only": True}}
