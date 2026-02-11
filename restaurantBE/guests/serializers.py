"""
Guest Serializers
Handles: Guest data serialization and login (which creates new guest)
"""
from restaurantBE.constants.roles import TableStatus
from rest_framework_simplejwt.settings import api_settings
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from restaurantBE.guests.models import Guest
from restaurantBE.tables.models import Table
from restaurantBE.constants.roles import Role


class GuestSerializer(serializers.ModelSerializer):
    """Basic Guest serializer"""
    
    tableNumber = serializers.IntegerField(source='tableNumber_id', read_only=True)
    
    class Meta:
        model = Guest
        fields = ['id', 'name', 'tableNumber', 'create_at', 'update_at']
        read_only_fields = ['id', 'create_at', 'update_at']


class GuestCreateAccountSerializer(serializers.Serializer):
    """
    Base serializer for creating Guest account
    Only creates guest without authentication tokens
    
    Required fields:
    - name: Guest name
    - tableNumber: Table number (ID)
    """
    
    name = serializers.CharField(required=True, max_length=100)
    tableNumber = serializers.IntegerField(required=True)
    
    def validate_name(self, value):
        """Validate guest name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(_("name_too_short"))
        return value.strip()
    
    def validate_tableNumber(self, value):
        """Validate table exists"""
        try:
          table =  Table.objects.get(number=value)
          if table.status != TableStatus.AVAILABLE:
            raise serializers.ValidationError(_('table_not_available'))
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('table_not_found'))
        return value
    
    def create_guest(self, validated_data):
        """
        Create new guest instance
        Can be overridden by child classes
        """
        name = validated_data.get('name')
        table_number = validated_data.get('tableNumber')
        
        # Create new guest
        guest = Guest.objects.create(
            name=name,
            tableNumber_id=table_number
        )
        # update status
        table = Table.objects.get(number=table_number)
        table.status = TableStatus.RESERVED
        table.save()
        return guest
    
    def validate(self, attrs):
        """
        Create new guest account
        """
        guest = self.create_guest(attrs)
        
        return {
            'guest': GuestSerializer(guest).data
        }


class GuestLoginSerializer(GuestCreateAccountSerializer):
    """
    Guest Login Serializer (extends GuestCreateAccountSerializer)
    Adds tableToken validation and JWT token generation
    
    Required fields:
    - name: Guest name (inherited)
    - tableNumber: Table number (inherited)
    - tableToken: Token to verify table access (new)
    """
    
    tableToken = serializers.CharField(required=True, max_length=255)
    
    def validate_tableToken(self, value):
        """Validate table token is provided"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(_("table_token_required"))
        return value.strip()
    
    def validate(self, attrs):
        """
        Validate table token and create new guest session with JWT tokens
        """
        table_number = attrs.get('tableNumber')
        table_token = attrs.get('tableToken')
        
        # Verify table exists and token is correct
        try:
            table = Table.objects.get(number=table_number)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'tableNumber': _('table_not_found')})
        
        # Verify table token
        if table.token != table_token:
            raise serializers.ValidationError({'tableToken': _('invalid_table_token')})

        # Create new guest using parent method
        guest = self.create_guest(attrs)
        
        # Generate JWT tokens with custom claims
        refresh = RefreshToken()
        refresh['guest_id'] = guest.id
        refresh['role'] = Role.GUEST
        
        return {
            'refreshToken': str(refresh),
            'accessToken': str(refresh.access_token),
            'guest': guest
        }


class GuestRefreshTokenSerializer(serializers.Serializer):
    """Refresh token serializer for guests"""
    
    refreshToken = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate and refresh token"""
        refresh_token_str = attrs.get('refreshToken')
        
        try:
            refresh = RefreshToken(refresh_token_str)
            
            # Verify this is a guest token
            if refresh.get('role') != Role.GUEST:
                raise serializers.ValidationError(_('invalid_guest_token'))
            
            # Verify guest still exists
            guest_id = refresh.get('guest_id')
            if not Guest.objects.filter(id=guest_id).exists():
                raise serializers.ValidationError(_('guest_not_found'))
            
            # Generate new access token
            return {
                'accessToken': str(refresh.access_token),
                'refreshToken': str(refresh),
            }
            
        except TokenError:
            raise serializers.ValidationError(_('token_invalid'))
