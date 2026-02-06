from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.translation import gettext_lazy as _

from restaurantBE.utils.responses import apiError


def CustomExceptionHandler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, (InvalidToken, TokenError)):
        return apiError(
            errors=response.data,
            msg="token_invalid",
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return apiError(
            errors=response.data,
            msg="unauthorized",
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        return apiError(
            errors=response.data,
            msg="bad_request",
            status=status.HTTP_400_BAD_REQUEST,
        )

    if response.status_code == status.HTTP_403_FORBIDDEN:
        msg = response.data.get("detail", "permission_denied")
        if isinstance(msg, list) and len(msg) > 0:
            msg = msg[0]
            
        return apiError(
            errors=None,
            msg=str(msg),
            status=status.HTTP_403_FORBIDDEN,
        )

    return response
