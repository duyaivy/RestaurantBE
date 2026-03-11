"""
Guest URLs Configuration
"""

from django.urls import path
from restaurantBE.orders.views import (
    OrderListAPIView,
    OrderCreateAPIView,
    OrderRetrieveUpdateDestroyAPIView,
    OrderUpdateStatusAPIView,
)

urlpatterns = [
    # Guest Authentication (Login creates new guest)
    path("orders/guest-create/", OrderCreateAPIView.as_view(), name="orders-guest-create"),
    path("orders/staff-create/", OrderCreateAPIView.as_view(), name="orders-staff-create"),
    path("orders/", OrderListAPIView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderRetrieveUpdateDestroyAPIView.as_view(), name="order-detail"),
    path("orders/<int:pk>/status/", OrderUpdateStatusAPIView.as_view(), name="order-update-status"),
]
