

"""
Table URLs Configuration
"""

from django.urls import path
from restaurantBE.tables.views import (
    TableRetrieveListAPIView,
    TableRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('tables/', TableRetrieveListAPIView.as_view(), name='table-list'),
    path('tables/<int:number>/', TableRetrieveUpdateDestroyAPIView.as_view(), name='table-detail'),
]
