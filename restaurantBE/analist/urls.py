from django.urls import path

from restaurantBE.analist.views import AnalistPingAPIView

urlpatterns = [
    path("analists/", AnalistPingAPIView.as_view(), name="analist-ping"),
]

