from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurantBE.users.views import (
    RegistrationAPIView,
    UserAPIViewSet,
)

router = DefaultRouter()
router.register(r"users", UserAPIViewSet)

urlpatterns = [
    path("auth/register/", RegistrationAPIView.as_view(), name="user_register"),
    path("", include(router.urls), name="users"),
]
