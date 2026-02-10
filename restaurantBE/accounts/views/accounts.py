"""
User Management Views
Handles: Get User Profile, Update Profile, Change Password
"""

from django.http.response import Http404
from rest_framework.generics import ListCreateAPIView
from restaurantBE.utils.custom_pagination import CustomPagination
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from restaurantBE.accounts.serializers import AccountSerializer
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework.generics import ListCreateAPIView
from restaurantBE.accounts.models import Account
from django.utils.translation import gettext_lazy as _

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
        if "password" in request.data or "email" in request.data or "id" in request.data:
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
                    serializer.data,
                    "update_user_success",
                    status=status.HTTP_200_OK
                )
            return apiError(
                serializer.errors,
                "validation_error",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
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
                return apiError({
                    "old_password": ["password_incorrect"]
                }, "password_incorrect", status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            if new_password != confirm_password:
                return apiError({
                    "confirm_password": ["confirm_password_not_match"]
                }, "confirm_password_not_match", status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            user.set_password(new_password)
            user.save()
            return apiSuccess(None, "change_password_success", status.HTTP_200_OK)
        except Exception as e:
            return apiError(str(e), "change_password_failed", status.HTTP_400_BAD_REQUEST)

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
        response = super().list(request, *args, **kwargs)
        return apiSuccess(
            data=response.data,
            msg=_("get_employees_success"),
            status=status.HTTP_200_OK,
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
    serializer_class = AccountSerializer
    queryset = Account.objects.filter(role=Role.EMPLOYEE)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return apiError(
                None,
                _("employee_not_found"),
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(instance)
        return apiSuccess(
            data=serializer.data,
            msg=_("get_employee_success"),
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        """
        Update Employee - Prevent email, password, id changes
        """
        try:
            instance = self.get_object()
        except Http404:
            return apiError(
                None,
                _("employee_not_found"),
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        
        if "email" in data:
            del data["email"]
        
        data["email"] = instance.email
      
        serializer = self.get_serializer(instance, data=data, partial=kwargs.get('partial', False))
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

    def partial_update(self, request, *args, **kwargs):
        """
        Partial Update Employee (PATCH)
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete Employee
        """
        try:
            instance = self.get_object()
        except Http404:
            return apiError(
                None,
                _("employee_not_found"),
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return apiSuccess(
            data=None,
            msg=_("delete_employee_success"),
            status=status.HTTP_200_OK,
        )