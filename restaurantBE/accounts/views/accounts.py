"""
User Management Views
Handles: Get User Profile, Update Profile, Change Password
"""

from restaurantBE.accounts.serializers.accounts import AccountUpdateSerializer
from django.http.response import Http404
from rest_framework.generics import ListCreateAPIView
from restaurantBE.utils.custom_pagination import CustomPagination
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from restaurantBE.accounts.serializers import AccountSerializer
from restaurantBE.utils.responses import apiError, apiSuccess
from restaurantBE.accounts.models import Account
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class AccountAPIView(generics.GenericAPIView):
    """
    Get & Update Current User Profile
    GET /api/me/
    PATCH /api/me/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_object(self):
        return self.request.user

    def get(self, request):
        try:
            serializer = self.get_serializer(self.get_object())
            return apiSuccess(
                serializer.data,
                "get_user_success",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return apiError(
                str(e),
                "user_not_found",
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request):
        # check not pw and email
        if (
            "password" in request.data
            or "email" in request.data
            or "id" in request.data
        ):
            return apiError(
                None,
                "update_restricted_fields",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                # save to db
                serializer.save()
                return apiSuccess(
                    serializer.data, "update_user_success", status=status.HTTP_200_OK
                )
            return apiError(
                serializer.errors,
                "validation_error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            return apiError(
                str(e),
                "update_user_failed",
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordAPIView(generics.GenericAPIView):
    """
    Change Password
    POST /api/account/change-password/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = self.request.user
            old_password = request.data.get("old_password")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            if not user.check_password(old_password):
                return apiError(
                    {"old_password": ["password_incorrect"]},
                    "password_incorrect",
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            if new_password != confirm_password:
                return apiError(
                    {"confirm_password": ["confirm_password_not_match"]},
                    "confirm_password_not_match",
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            user.set_password(new_password)
            user.save()
            return apiSuccess(None, "change_password_success", status.HTTP_200_OK)
        except Exception as e:
            return apiError(
                str(e), "change_password_failed", status.HTTP_400_BAD_REQUEST
            )


from restaurantBE.constants import Role


from restaurantBE.utils.permissions import IsAdmin


class EmployeeListCreateAPIView(ListCreateAPIView):
    """
    Get All Employees + Create New Employee
    GET /api/accounts?page=1&limit=10
    POST /api/accounts
    """

    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        """
        Automatically set role to EMPLOYEE when creating new account
        """
        serializer.save(role=Role.EMPLOYEE)

    def get_queryset(self):
        return Account.objects.filter(role=Role.EMPLOYEE)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            try:
                page = self.paginate_queryset(queryset)
            except ValidationError as e:
                return apiError(
                    e.detail,
                    msg=_("invalid_page_number"),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if page is not None:
                serializer = self.get_serializer(page, many=True)

                current_page = self.paginator.page.number
                total_pages = self.paginator.page.paginator.num_pages

                resData = {
                    "count": total_pages,
                    "current": current_page,
                    "results": serializer.data,
                }

                return apiSuccess(resData, msg=_("get_employees_success"))

            serializer = self.get_serializer(queryset, many=True)
            return apiSuccess(serializer.data, msg=_("get_employees_success"))

        except Exception as e:
            logger.error(f"Error in EmployeeListCreateAPIView.list: {str(e)}")
            return apiError(
                None,
                msg=_("get_employees_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return apiSuccess(
            data=response.data,
            msg=_("create_employee_success"),
            status=status.HTTP_200_OK,
        )


class EmployeeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, Update, Delete Employee by ID
    GET /api/accounts/<id>/
    PUT /api/accounts/<id>/
    DELETE /api/accounts/<id>/
    """

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AccountUpdateSerializer
    queryset = Account.objects.filter(role=Role.EMPLOYEE)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return apiSuccess(
                data=serializer.data,
                msg=_("get_employee_success"),
                status=status.HTTP_200_OK,
            )
        except Http404:
            return apiError(
                None,
                _("employee_not_found"),
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error in EmployeeDetailAPIView.retrieve: {str(e)}")
            return apiError(
                None,
                _("get_employee_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        """
        Update Employee Information
        - Email: Cannot be changed (read-only)
        - Password: Optional, admin can reset employee password
        - Name, Avatar: Can be updated
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=kwargs.get("partial", False)
            )

            if serializer.is_valid():
                serializer.save()
                return apiSuccess(
                    data=serializer.data,
                    msg=_("update_employee_success"),
                    status=status.HTTP_200_OK,
                )

            return apiError(
                serializer.errors,
                _("validation_error"),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Http404:
            return apiError(
                None,
                _("employee_not_found"),
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error in EmployeeDetailAPIView.update: {str(e)}")
            return apiError(
                None,
                _("update_employee_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def partial_update(self, request, *args, **kwargs):
        """
        Partial Update Employee (PATCH)
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete Employee
        """
        try:
            instance = self.get_object()
            instance.delete()
            return apiSuccess(
                data=None,
                msg=_("delete_employee_success"),
                status=status.HTTP_200_OK,
            )
        except Http404:
            return apiError(
                None,
                _("employee_not_found"),
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error in EmployeeDetailAPIView.destroy: {str(e)}")
            return apiError(
                None,
                _("delete_employee_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )
