from restaurantBE.accounts.views.accounts import EmployeeListAPIView
from restaurantBE.accounts.views.accounts import AccountAPIView
from django.urls import path

from restaurantBE.accounts.views.auth import LogoutAPIView, RefreshTokenAPIView
from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ChangePasswordAPIView,
)


urlpatterns = [
    # Authentication
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/refresh-token/", RefreshTokenAPIView.as_view(), name="refresh_token"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    # User Management
    path("me/", AccountAPIView.as_view(), name="get_user"),
    path("me/update/", AccountAPIView.as_view(), name="update_user"),
    path("me/change-password/", ChangePasswordAPIView.as_view(), name="change_password"),

    # Employee Management
    path("accounts/", EmployeeListAPIView.as_view(), name="get_employees"),
    # path("accounts/<int:pk>/", EmployeeDetailAPIView.as_view(), name="get_employee"),
    # path("accounts/<int:pk>/update/", EmployeeDetailAPIView.as_view(), name="update_employee"),
    # path("accounts/<int:pk>/delete/", EmployeeDetailAPIView.as_view(), name="delete_employee"),

]
