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
    EmployeeListCreateAPIView,
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
    "EmployeeListCreateAPIView",
    "EmployeeDetailAPIView",
]
