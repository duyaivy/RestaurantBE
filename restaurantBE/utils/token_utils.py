"""
Token Utilities
Utility functions for JWT token persistence and blacklist support.
"""

from __future__ import annotations

import logging
from typing import Optional

from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

logger = logging.getLogger(__name__)


def persist_tokens_to_outstanding(
    refresh_token_str: Optional[str] = None,
    access_token_str: Optional[str] = None,
    user_id: Optional[int] = None,
    *,
    is_guest: bool = False,
) -> None:
    """
    Lưu refresh và access token vào OutstandingToken table.
    Silent failure — không block login flow nếu lỗi.
    """
    try:
        # Lưu refresh token
        if refresh_token_str:
            refresh_token = RefreshToken(refresh_token_str)
            jti_refresh = refresh_token["jti"]
            resolved_user_id = user_id if user_id is not None else refresh_token.get(
                "guest_id" if is_guest else "user_id"
            )

            if not OutstandingToken.objects.filter(jti=jti_refresh).exists():
                OutstandingToken.objects.create(
                    user_id=resolved_user_id,
                    jti=jti_refresh,
                    token=str(refresh_token),
                    created_at=timezone.now(),
                    expires_at=timezone.datetime.fromtimestamp(
                        refresh_token["exp"], tz=timezone.utc
                    ),
                )

        # Lưu access token
        if access_token_str:
            access_token = AccessToken(access_token_str)
            jti_access = access_token["jti"]
            resolved_user_id = user_id if user_id is not None else access_token.get(
                "guest_id" if is_guest else "user_id"
            )

            if not OutstandingToken.objects.filter(jti=jti_access).exists():
                OutstandingToken.objects.create(
                    user_id=resolved_user_id,
                    jti=jti_access,
                    token=str(access_token),
                    created_at=timezone.now(),
                    expires_at=timezone.datetime.fromtimestamp(
                        access_token["exp"], tz=timezone.utc
                    ),
                )
    except Exception as e:
        logger.warning(f"Failed to save outstanding token: {str(e)}")
