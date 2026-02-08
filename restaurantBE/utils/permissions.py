from rest_framework.permissions import BasePermission
from restaurantBE.constants import Role

class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """
    message = "admin_required"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ADMIN)
    
class IsEmployee(BasePermission):
    """
    Allows access only to employee users.
    """
    message = "employee_required"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.EMPLOYEE)
