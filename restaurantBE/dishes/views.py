from re import search

from django.http.response import Http404
from restaurantBE.constants.roles import DishStatus
from restaurantBE.utils.custom_filter import DishFilter
from restaurantBE.utils.custom_pagination import CustomPagination
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework import status
from rest_framework.exceptions import ValidationError
from restaurantBE.utils.permissions import IsAdminOrEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from restaurantBE.dishes.models import Dish
from restaurantBE.dishes.serializers import DishSerializer
import logging
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

logger = logging.getLogger(__name__)


class DishListCreateAPIView(ListCreateAPIView):
    queryset = Dish.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    serializer_class = DishSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DishFilter

    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]  # default
    search_fields = ["name__vi", "name__en"]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            try:
                page = self.paginate_queryset(queryset)
            except ValidationError as e:
                return apiError(
                    e.detail,
                    msg=_("invalid_page_number"),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if page is not None:
                serializer = self.get_serializer(page, many=True)

                current_page = self.paginator.page.number
                total_pages = self.paginator.page.paginator.num_pages

                resData = {
                    "count": total_pages,
                    "current": current_page,
                    "results": serializer.data,
                }

                return apiSuccess(resData, msg=_("get_all_dish_success"))

            serializer = self.get_serializer(queryset, many=True)
            return apiSuccess(serializer.data, msg=_("get_all_dish_success"))

        except Exception as e:
            return apiError(
                None,
                msg=_("get_all_dish_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Create dish
                dish = serializer.save()
                response_serializer = DishSerializer(dish)
                return apiSuccess(
                    response_serializer.data, msg=_("create_dish_success")
                )

            return apiError(
                serializer.errors,
                msg=_("create_dish_error"),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("create_dish_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class DishRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return apiSuccess(serializer.data, msg=_("get_dish_success"))
        except Http404:
            return apiError(
                None, msg=_("dish_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:

            return apiError(
                None,
                msg=_("get_dish_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return apiSuccess(None, msg=_("delete_dish_success"))
        except Http404:
            return apiError(
                None, msg=_("dish_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("delete_dish_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return apiSuccess(serializer.data, msg=_("update_dish_success"))

            return apiError(
                serializer.errors,
                msg=_("update_dish_error"),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Http404:
            return apiError(
                None, msg=_("dish_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return apiError(
                None,
                msg=_("update_dish_error"),
                status=status.HTTP_400_BAD_REQUEST,
            )
