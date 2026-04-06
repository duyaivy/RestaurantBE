"""
Guest URLs Configuration
"""

from restaurantBE.orders.views import VerifyOrderVNpayView
from django.urls import path
from restaurantBE.orders.views import (
    OrderListAPIView,
    OrderCreateAPIView,
    OrderStaffCreateAPIView,
    OrderRetrieveDestroyAPIView,
    OrderUpdateStatusAPIView,
    OrderUpdateAPIView,
    OrderUpdateItemsAPIView,
    OrderCreatePaymentView,
    GuestOrderListAPIView
)

urlpatterns = [
    # Order List & Create
    path("orders/", OrderListAPIView.as_view(), name="orders-list"),
    # Guest create order
    path(
        "orders/guest-create/", OrderCreateAPIView.as_view(), name="orders-guest-create"
    ),
    # Guest get orders
    path(
        "orders/guest/<int:guest_id>/", GuestOrderListAPIView.as_view(), name="orders-guest-list"
    ),
    # Staff create order (for guest)
    path(
        "orders/staff-create/",
        OrderStaffCreateAPIView.as_view(),
        name="orders-staff-create",
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
    path("orders/verify/", VerifyOrderVNpayView.as_view(), name="order-verify"),
    path("orders/<int:pk>/payment/", OrderCreatePaymentView.as_view(), name="order-vnpay-create-payment"),
]
