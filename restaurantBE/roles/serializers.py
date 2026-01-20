from rest_framework import serializers

from .models import Role


class RoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)

    class Meta:
        model = Role
        fields = ("id", "name")
