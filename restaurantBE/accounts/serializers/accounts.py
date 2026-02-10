from rest_framework import serializers
from restaurantBE.accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "name", "email", "avatar", "role", "create_at", "update_at")
        read_only_fields = ("id", "role", "create_at", "update_at")

class AccountUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating employee information.
    - Email: Read-only, cannot be changed to prevent account hijacking
    - Password: Optional, will be hashed if provided (admin can reset employee password)
    - Name, Avatar: Can be updated freely
    """
    password = serializers.CharField(
        write_only=True, 
        required=False,
        allow_blank=False,
        min_length=6,
        help_text="Optional. If provided, employee password will be updated (must be at least 6 characters)"
    )
    
    class Meta:
        model = Account
        fields = ("id", "name", "email", "password", "avatar", "role", "create_at", "update_at")
        read_only_fields = ("id", "email", "role", "create_at", "update_at")
    
    def update(self, instance, validated_data):
        """
        Update employee information.
        Password is hashed using set_password() for security.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        
        password = validated_data.get("password")
        if password:
            instance.set_password(password) 
        
        instance.save()
        return instance