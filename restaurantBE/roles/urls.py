from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurantBE.roles.views import RoleAPIViewSet

router = DefaultRouter()
router.register(r"roles", RoleAPIViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
