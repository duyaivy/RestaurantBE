"""
Guest URLs Configuration
"""

from django.urls import path
from restaurantBE.orders.views import (
    OrderListAPIView,
    OrderCreateAPIView,
    OrderRetrieveDestroyAPIView,
    OrderUpdateStatusAPIView,
    OrderUpdateAPIView,
    OrderUpdateItemsAPIView,
)

urlpatterns = [
    # Order List & Create
    path("orders/", OrderListAPIView.as_view(), name="orders-list"),
    # Guest create order
    path(
        "orders/guest-create/", OrderCreateAPIView.as_view(), name="orders-guest-create"
    ),
    path(
        "orders/staff-create/", OrderCreateAPIView.as_view(), name="orders-staff-create"
    ),
    path(
        "orders/<int:pk>/", OrderRetrieveDestroyAPIView.as_view(), name="order-detail"
    ),
    path("orders/<int:pk>/update/", OrderUpdateAPIView.as_view(), name="order-update"),
    path(
        "orders/<int:pk>/status/",
        OrderUpdateStatusAPIView.as_view(),
        name="order-update-status",
    ),
    # Order items update - PATCH để add/cancel dishes
    path(
        "orders/<int:pk>/items/",
        OrderUpdateItemsAPIView.as_view(),
        name="order-update-items",
    ),
]
