from rest_framework import generics, status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated


from restaurantBE.utils.pagination.custom_pagination import CustomPagination

from .models import User
from .serializers import RegistrationSerializer, UserSerializer


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializers = {"default": UserSerializer}
    pagination_class = CustomPagination

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        url_name="me",
        pagination_class=None,
    )
    def get_current_user(self, request):
        try:
            return Response(
                UserSerializer(
                    self.request.user, context={"request": self.request}
                ).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": "Wrong auth token"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=["GET"],
        url_path="guarded",
        url_name="guarded",
        pagination_class=None,
        permission_classes=[IsAuthenticated],
    )
    def guarded(self, request):
        return Response(
            {"message": "You are authenticated!"},
            status=status.HTTP_200_OK,
        )
