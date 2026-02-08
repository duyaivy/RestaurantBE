"""
Export all views from submodules
Usage: from restaurantBE.accounts.views import RegisterAPIView
"""

from .auth import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
)

from .accounts import (
    AccountAPIView,
    ChangePasswordAPIView,
    EmployeeListAPIView,
    EmployeeDetailAPIView
)

__all__ = [
    # Authentication
    "RegisterAPIView",
    "LoginAPIView",
    "LogoutAPIView",
    # User Management
    "AccountAPIView",
    "ChangePasswordAPIView",
    "EmployeeListAPIView",
    "EmployeeDetailAPIView",
]
