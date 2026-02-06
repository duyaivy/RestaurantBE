"""
User Management Views
Handles: Get User Profile, Update Profile, Change Password
"""

from restaurantBE.utils.custom_pagination import CustomPagination
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from restaurantBE.accounts.serializers import AccountSerializer
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework.generics import ListAPIView
from restaurantBE.accounts.models import Account

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

class EmployeeListAPIView(ListAPIView):
    """
    Get All Employees + pagination
    GET /api/accounts?page=1&limit=10
    """
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AccountSerializer
    queryset = Account.objects.filter(role=Role.EMPLOYEE)


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
