from django.http.response import Http404
from restaurantBE.constants.choices import DishStatus
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework import status
from restaurantBE.utils.permissions import IsAdminOrEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from restaurantBE.categories.models import Category
from restaurantBE.categories.serializers import CategorySerializer
import logging
from django.utils.translation import gettext as _
from restaurantBE.dishes.models import Dish
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class CategoryRetrieveListAPIView(ListCreateAPIView):
    """
    API view for listing all categories and creating new category
    GET /categories/ - Get all categories
    POST /categories/ - Create new category
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    authentication_classes = []

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    # permission_classes = []
    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated(), IsAdminOrEmployee()]

    def list(self, request, *args, **kwargs):
        """Get all categories"""
        data = self.get_queryset().all()
        serializer = self.get_serializer(data, many=True)
        return apiSuccess(serializer.data, msg=_("get_all_categories_success"))

    def post(self, request, *args, **kwargs):
        """Create a new category"""
        serializer = self.get_serializer(data=request.data)
        logger.info(serializer)
        if serializer.is_valid():
            # Create category
            category = serializer.save()

            # Serialize full category object to return all fields
            response_serializer = CategorySerializer(category)
            return apiSuccess(
                response_serializer.data, msg=_("create_category_success")
            )

        return apiError(
            serializer.errors,
            msg=_("create_category_error"),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific category
    GET /categories/<id>/ - Get category by id
    PATCH /categories/<id>/ - Update category
    DELETE /categories/<id>/ - Soft delete category (set isActive to False)
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrEmployee]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def retrieve(self, request, *args, **kwargs):
        """Get category by id"""
        try:
            instance = self.get_object()
        except Http404:
            return apiError(
                None, msg=_("category_not_found"), status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        dishData = Dish.objects.filter(
            category_id=instance.id, status=DishStatus.AVAILABLE
        ).values()
        res = {**serializer.data, "dishes": dishData}
        return apiSuccess(
            res,
            msg=_("get_category_success"),
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete category by setting isActive to False"""
        try:
            instance = self.get_object()
        except Http404:
            return apiError(
                None, msg=_("category_not_found"), status=status.HTTP_404_NOT_FOUND
            )

        # Soft delete
        instance.is_active = False
        instance.save()

        return apiSuccess(None, msg=_("delete_category_success"))

    def update(self, request, *args, **kwargs):
        """Update category"""
        try:
            instance = self.get_object()
        except Http404:
            return apiError(
                None, msg=_("category_not_found"), status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return apiSuccess(serializer.data, msg=_("update_category_success"))

        return apiError(
            serializer.errors,
            msg=_("update_category_error"),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
