from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="RestaurantBE API",
        default_version="v1",
        contact=openapi.Contact(email="dscdut@gmail.com"),
    ),
    url=settings.HOST + "api/",
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    # swagger docs
    re_path(
        r"^docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("admin/", admin.site.urls),
    # api route
    path("api/auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/auth/refresh-token/", TokenRefreshView.as_view(), name="refresh_token"),
    path("api/", include("restaurantBE.users.urls"), name="users"),
    path("api/", include("restaurantBE.roles.urls"), name="roles"),
]
