"""
Dish URLs Configuration
"""

from django.urls import path
from restaurantBE.dishes.views import (
    DishListCreateAPIView,
    DishRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("dishes/", DishListCreateAPIView.as_view(), name="dish-list"),
    path(
        "dishes/<int:pk>/",
        DishRetrieveUpdateDestroyAPIView.as_view(),
        name="dish-detail",
    ),
]
