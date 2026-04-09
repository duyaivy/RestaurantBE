from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework import permissions

from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    db_status = "ok"
    try:
        connection.ensure_connection()
    except Exception:
        db_status = "error"
    return JsonResponse({"status": "ok", "db": db_status})


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
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
    # api route
    path("api/", include("restaurantBE.accounts.urls"), name="accounts"),
    path("api/", include("restaurantBE.upload.urls"), name="upload"),
    path("api/", include("restaurantBE.guests.urls"), name="guests"),
    path("api/", include("restaurantBE.tables.urls"), name="tables"),
    path("api/", include("restaurantBE.dishes.urls"), name="dishes"),
    path("api/", include("restaurantBE.categories.urls"), name="categories"),
    path("api/", include("restaurantBE.orders.urls"), name="orders"),
    path("api/", include("restaurantBE.analist.urls"), name="analist"),
    path("api/", include("restaurantBE.chatbot.urls"), name="chatbot"),
]
