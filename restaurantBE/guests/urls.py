"""
Guest URLs Configuration
"""

from django.urls import path
from restaurantBE.guests.views import (
    GuestLoginAPIView,
    GuestLogoutAPIView,
    GuestRefreshTokenAPIView,
    GuestCreateAccountAPIView,
)

urlpatterns = [
    # Guest Authentication (Login creates new guest)
    path('guests/login/', GuestLoginAPIView.as_view(), name='guest-login'),
    path('guests/logout/', GuestLogoutAPIView.as_view(), name='guest-logout'),
    path('guests/refresh-token/', GuestRefreshTokenAPIView.as_view(), name='guest-refresh-token'),
    path("accounts/guests/", GuestCreateAccountAPIView.as_view(), name='guest-create-account'),
]

