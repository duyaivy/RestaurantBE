"""
Guest URLs Configuration
"""

from django.urls import path
from restaurantBE.guests.views import (
    GuestLoginAPIView,
    GuestLogoutAPIView,
    GuestMessageAPIView,
    GuestRefreshTokenAPIView,
    GuestCreateAccountAPIView,
)

urlpatterns = [
    # Guest Authentication (Login creates new guest)
    path("guests/login/", GuestLoginAPIView.as_view(), name="guest-login"),
    path("guests/logout/", GuestLogoutAPIView.as_view(), name="guest-logout"),
    path(
        "guests/refresh-token/",
        GuestRefreshTokenAPIView.as_view(),
        name="guest-refresh-token",
    ),
    path(
        "accounts/guests/",
        GuestCreateAccountAPIView.as_view(),
        name="guest-create-account",
    ),
    path("guests/message/", GuestMessageAPIView.as_view(), name="guest-message"),
]

# ### 4. Đặt món (Guest)

# - **Endpoint:** `POST /guest/orders`
# - **Mô tả:** Khách tự đặt món
# - **Auth Required:** ✅ (Guest token)
# - **Body:** (Lưu ý: Body là array trực tiếp, không phải object)
#   ```json
#   [
#     {
#       "dishId": "number",
#       "quantity": "number"
#     }
#   ]
#   ```
# - **Socket Event:** `new-order` (broadcast đến manager)
# - **Response:**
#   ```json
#   {
#     "message": "Đặt món thành công",
#     "data": ["Array of Order objects (xem Order Schema)"]
#   }
#   ```

# ### 5. Lấy đơn hàng của tôi (Guest)

# - **Endpoint:** `GET /guest/orders`
# - **Mô tả:** Khách xem đơn hàng của mình
# - **Auth Required:** ✅ (Guest token)
# - **Response:**
#   ```json
#   {
#     "message": "Lấy danh sách đơn hàng thành công",
#     "data": ["Array of Order objects (xem Order Schema)"]
#   }
#   ```
