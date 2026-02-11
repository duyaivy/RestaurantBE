"""
Custom Authentication Classes
Supports both Account (User) and Guest authentication
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist

from restaurantBE.accounts.models import Account
from restaurantBE.guests.models import Guest
from restaurantBE.constants.roles import Role


class GuestJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication for Guest
    Validates JWT tokens and retrieves Guest user
    """
    
    def get_user(self, validated_token):
        """
        Retrieve Guest user from validated token
        """
        try:
            role = validated_token.get('role')
            
            # Ensure this is a guest token
            if role != Role.GUEST:
                raise AuthenticationFailed(_('invalid_guest_token'))
            
            guest_id = validated_token.get('guest_id')
            
            if guest_id is None:
                raise AuthenticationFailed(_('token_invalid'))
            
            try:
                guest = Guest.objects.get(id=guest_id)
            except ObjectDoesNotExist:
                raise AuthenticationFailed(_('guest_not_found'))
            
            if not guest.is_active:
                raise AuthenticationFailed(_('guest_inactive'))
            
            return guest
            
        except AuthenticationFailed:
            raise
        except Exception as e:
            raise AuthenticationFailed(str(e))


class AccountJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication for Account (regular users)
    Validates JWT tokens and retrieves Account user
    """
    
    def get_user(self, validated_token):
        """
        Retrieve Account user from validated token
        """
        try:
            role = validated_token.get('role')
            
            # Ensure this is NOT a guest token
            if role == Role.GUEST:
                raise AuthenticationFailed(_('invalid_account_token'))
            
            user_id = validated_token.get('user_id')
            
            if user_id is None:
                raise AuthenticationFailed(_('token_invalid'))
            
            try:
                user = Account.objects.get(id=user_id)
            except ObjectDoesNotExist:
                raise AuthenticationFailed(_('user_not_found'))
            
            if not user.is_active:
                raise AuthenticationFailed(_('user_inactive'))
            
            return user
            
        except AuthenticationFailed:
            raise
        except Exception as e:
            raise AuthenticationFailed(str(e))

