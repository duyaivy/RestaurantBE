"""
Category URLs Configuration
"""

from django.urls import path
from restaurantBE.categories.views import (
    CategoryRetrieveListAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("categories/", CategoryRetrieveListAPIView.as_view(), name="category-list"),
    path(
        "categories/<int:id>/",
        CategoryRetrieveUpdateDestroyAPIView.as_view(),
        name="category-detail",
    ),
]
