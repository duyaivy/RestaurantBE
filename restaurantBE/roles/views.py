from rest_framework import mixins, viewsets
from restaurantBE.utils.pagination.custom_pagination import CustomPagination
from .models import Role
from .serializers import RoleSerializer


class RoleAPIViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Role.objects.all()
    serializers = {"default": RoleSerializer}
    pagination_class = CustomPagination

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
