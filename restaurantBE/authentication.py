"""
Custom Authentication Classes
Supports both Account (User) and Guest authentication

Cách hoạt động:
- authenticate() kiểm tra role trong token, nếu sai loại thì return None
  (DRF sẽ thử class tiếp theo, KHÔNG raise lỗi)
- get_user() validate chi tiết token, nếu lỗi thì raise AuthenticationFailed
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist

from restaurantBE.accounts.models import Account
from restaurantBE.guests.models import Guest
from restaurantBE.constants.choices import Role


class GuestJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication for Guest
    Validates JWT tokens and retrieves Guest user
    """
    
    def authenticate(self, request):
        """
        Chỉ xử lý token có role=GUEST.
        Token khác loại -> return None để DRF thử class tiếp theo.
        """
        header = self.get_header(request)
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        
        # Không phải guest token -> bỏ qua, để class khác xử lý
        role = validated_token.get('role')
        if role != Role.GUEST:
            return None
        
        # Đúng guest token -> validate chi tiết
        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        """
        Retrieve Guest user from validated token.
        Tới đây nghĩa là token đã đúng role GUEST, chỉ cần validate guest_id.
        """
        try:
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
    
    def authenticate(self, request):
        """
        Chỉ xử lý token KHÔNG phải Guest.
        Token guest -> return None để GuestJWTAuthentication xử lý.
        """
        header = self.get_header(request)
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        
        # Token guest -> bỏ qua, để GuestJWTAuthentication xử lý
        role = validated_token.get('role')
        if role == Role.GUEST:
            return None
        
        # Token account -> validate chi tiết
        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        """
        Retrieve Account user from validated token.
        Tới đây nghĩa là token đúng loại Account, chỉ cần validate user_id.
        """
        try:
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
