"""
Authentication Views
Handles: Register, Login, Logout, Token Refresh
"""

import logging
from datetime import datetime
from requests import request
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from restaurantBE.accounts.serializers import (
    AccountSerializer,
    LoginSerializer,
    RegisterSerializer,
)
from django.utils.translation import gettext as _
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from restaurantBE.accounts.serializers.auth import RefreshTokenSerializer
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

logger = logging.getLogger(__name__)


class RegisterAPIView(generics.GenericAPIView):
    """
    User Registration
    POST /api/auth/register/
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return apiSuccess(
                AccountSerializer(user).data,
                "register_success",
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return apiError(
                e.detail,
                "validation_error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            return apiError(
                str(e),
                "register_failed",
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginAPIView(TokenObtainPairView):
    """
    User Login
    POST /api/auth/login/
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Lưu CẢ access và refresh token vào OutstandingToken để blacklist mechanism hoạt động
        if response.status_code == 200:
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                from django.utils import timezone

                refresh_token_str = response.data.get("refresh")
                access_token_str = response.data.get("access")

                # Lưu refresh token
                if refresh_token_str:
                    refresh_token = RefreshToken(refresh_token_str)
                    jti_refresh = refresh_token["jti"]

                    if not OutstandingToken.objects.filter(jti=jti_refresh).exists():
                        OutstandingToken.objects.create(
                            user_id=refresh_token["user_id"],
                            jti=jti_refresh,
                            token=str(refresh_token),
                            created_at=timezone.now(),
                            expires_at=timezone.datetime.fromtimestamp(
                                refresh_token["exp"], tz=timezone.utc
                            ),
                        )

                # Lưu access token (QUAN TRỌNG để logout hoạt động)
                if access_token_str:
                    access_token = AccessToken(access_token_str)
                    jti_access = access_token["jti"]

                    if not OutstandingToken.objects.filter(jti=jti_access).exists():
                        OutstandingToken.objects.create(
                            user_id=access_token["user_id"],
                            jti=jti_access,
                            token=str(access_token),
                            created_at=timezone.now(),
                            expires_at=timezone.datetime.fromtimestamp(
                                access_token["exp"], tz=timezone.utc
                            ),
                        )

            except Exception:
                # Silent failure or minimal log if needed
                pass

        return apiSuccess(
            data=response.data, msg="login_success", status=response.status_code
        )


class LogoutAPIView(generics.GenericAPIView):
    """
    User Logout - Blacklist all user tokens
    POST /api/accounts/logout/
    Headers: Authorization: Bearer <access_token>
    Body: { "refreshToken": "..." }
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        refreshToken = request.data.get("refreshToken")

        if not refreshToken:
            return apiError(
                {"refreshToken": [_("token_required")]},
                "token_required",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refreshToken)
            user_id = token["user_id"]

            # Blacklist ALL outstanding tokens of this user
            tokens = OutstandingToken.objects.filter(user_id=user_id)

            for t in tokens:
                BlacklistedToken.objects.get_or_create(token=t)

            return apiSuccess(
                None,
                "logout_success",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return apiError(
                str(e),
                "logout_failed",
            )


class RefreshTokenAPIView(TokenRefreshView):
    """
    Token Refresh
    POST /api/auth/refresh-token/
    """

    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return apiSuccess(
                data=response.data,
                msg="token_refresh_success",
                status=response.status_code,
            )
        except Exception as e:
            # Xử lý lỗi trả về dict object thay vì string
            errors = e.detail if hasattr(e, "detail") else str(e)
            return apiError(
                errors=errors,
                msg="token_refresh_failed",
                status=status.HTTP_400_BAD_REQUEST,
            )
