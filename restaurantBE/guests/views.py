"""
Guest Authentication Views
Handles: Guest Login (creates new guest), Logout, Token Refresh
"""

from rest_framework.permissions import IsAuthenticated
from restaurantBE.utils.permissions import IsAdminOrEmployee
from rest_framework.decorators import authentication_classes
import logging
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from django.utils.translation import gettext as _
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from restaurantBE.guests.models import Guest
from restaurantBE.guests.serializers import (
    GuestSerializer,
    GuestLoginSerializer,
    GuestRefreshTokenSerializer,
    GuestCreateAccountSerializer,
)
from restaurantBE.utils.responses import apiError, apiSuccess

logger = logging.getLogger(__name__)

class GuestLoginAPIView(generics.GenericAPIView):
    """
    Guest Login (Creates New Guest Session)
    POST /api/guests/login/
    
    Body: {
        "name": "Guest Name",
        "tableNumber": 1,
        "tableToken": "table_secret_token"
    }
    
    Response: {
        "refresh": "refresh_token",
        "access": "access_token",
        "guest": {
            "id": 1,
            "name": "Guest Name",
            "tableNumber": 1,
            "create_at": "2026-02-11T14:00:00Z",
            "update_at": "2026-02-11T14:00:00Z"
        }
    }
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = GuestLoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            #check valid
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            validated_data = serializer.validated_data
            guest = validated_data['guest']
            
            # Prepare response data
            response_data = {
                'refreshToken': validated_data['refreshToken'],
                'accessToken': validated_data['accessToken'],
                'guest': GuestSerializer(guest).data
            }
            
            # Save tokens to OutstandingToken for blacklist mechanism
            try:
               
                
                refresh_token_str = validated_data['refreshToken']
                access_token_str = validated_data['accessToken']
                
                # Save refresh token
                if refresh_token_str:
                    refresh_token = RefreshToken(refresh_token_str)
                    jti_refresh = refresh_token["jti"]
                    guest_id = refresh_token["guest_id"]
                    
                    if not OutstandingToken.objects.filter(jti=jti_refresh).exists():
                        OutstandingToken.objects.create(
                            user_id=guest_id,
                            jti=jti_refresh,
                            token=str(refresh_token),
                            created_at=timezone.now(),
                            expires_at=timezone.datetime.fromtimestamp(
                                refresh_token["exp"], tz=timezone.utc
                            ),
                        )
                
                # Save access token
                if access_token_str:
                    access_token = AccessToken(access_token_str)
                    jti_access = access_token["jti"]
                    guest_id = access_token["guest_id"]
                    
                    if not OutstandingToken.objects.filter(jti=jti_access).exists():
                        OutstandingToken.objects.create(
                            user_id=guest_id,
                            jti=jti_access,
                            token=str(access_token),
                            created_at=timezone.now(),
                            expires_at=timezone.datetime.fromtimestamp(
                                access_token["exp"], tz=timezone.utc
                            ),
                        )
            except Exception as e:
                logger.warning(f"Failed to save outstanding token: {str(e)}")
                # Silent failure - don't block login
                pass
            
            return apiSuccess(
                data=response_data,
                msg="guest_login_success",
                status=status.HTTP_200_OK,
            )
            
        except ValidationError as e:
            return apiError(
                e.detail,
                "validation_error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            logger.error(f"Guest login failed: {str(e)}")
            return apiError(
                str(e),
                "guest_login_failed",
                status=status.HTTP_400_BAD_REQUEST,
            )


class GuestLogoutAPIView(generics.GenericAPIView):
    """
    Guest Logout
    POST /api/guests/logout/
    
    Body: { "refreshToken": "..." }
    
    Clears the refresh token from database and blacklists all tokens
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refreshToken")

        if not refresh_token:
            return apiError(
                {"refreshToken": [_("token_required")]},
                _("token_required"),
                status=status.HTTP_400_BAD_REQUEST, 
            )

        try:
            token = RefreshToken(refresh_token)
            
            # Verify this is a guest token
            from restaurantBE.constants.roles import Role
            if token.get('role') != Role.GUEST:
                return apiError(
                    _("invalid_guest_token"),
                    _("invalid_guest_token"),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            guest_id = token["guest_id"]

            # Blacklist ALL outstanding tokens of this guest
            tokens = OutstandingToken.objects.filter(user_id=guest_id)

            for t in tokens:
                BlacklistedToken.objects.get_or_create(token=t)

            return apiSuccess(
                None,
                _("guest_logout_success"),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Guest logout failed: {str(e)}")
            return apiError(
                str(e),
                _("guest_logout_failed"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class GuestRefreshTokenAPIView(generics.GenericAPIView):
    """
    Guest Token Refresh
    POST /api/guests/refresh-token/
    
    Body: { "refresh": "..." }
    
    Validates refresh token against database and returns new access token
    """
    authentication_classes=[]
    permission_classes = [AllowAny]
    serializer_class = GuestRefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            return apiSuccess(
                data=serializer.validated_data,
                msg=_("guest_token_refresh_success"),
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return apiError(
                e.detail,
                "validation_error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            logger.error(f"Guest token refresh failed: {str(e)}")
            errors = e.detail if hasattr(e, "detail") else str(e)
            return apiError(
                errors=errors,
                msg=_("guest_token_refresh_failed"),
                status=status.HTTP_400_BAD_REQUEST,
            )

class GuestCreateAccountAPIView(generics.GenericAPIView):
    """
    Guest Create Account
    POST /api/guests/create-account/
    
    Body: { "name": "...",
    "tableNumber": "..." }
    """
  
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    serializer_class = GuestCreateAccountSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            return apiSuccess(
                data=serializer.validated_data,
                msg=_("guest_create_account_success"),
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return apiError(
                e.detail,
                "validation_error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            errors = e.detail if hasattr(e, "detail") else str(e)
            return apiError(
                errors=errors,
                msg=_("guest_create_account_failed"),
                status=status.HTTP_400_BAD_REQUEST,
            )