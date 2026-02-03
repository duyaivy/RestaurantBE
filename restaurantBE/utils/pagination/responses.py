from rest_framework.response import Response
from django.utils.translation import gettext as _


def apiSuccess(data=None, msg="success", status=200, code="success"):
    return Response(
        {
            "success": True,
            "code": code,
            "message": _(msg or code),
            "data": data,
        },
        status=status,
    )


def apiError(
    errors=None,
    msg="error",
    status=400,
    code="error",
):
    return Response(
        {
            "success": False,
            "code": code,
            "message": _(msg or code),
            "errors": errors,
        },
        status=status,
    )
