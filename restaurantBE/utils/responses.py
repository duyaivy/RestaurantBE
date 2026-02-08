from rest_framework.response import Response
from django.utils.translation import gettext as _


def apiSuccess(data=None, msg="success", status=200):
    return Response(
        {
            "success": True,
            "message": _(msg),
            "data": data,
        },
        status=status,
    )


def apiError(
    errors=None,
    msg="error",
    status=400,
):
    return Response(
        {
            "success": False,
            "message": _(msg),
            "errors": errors,
        },
        status=status,
    )
