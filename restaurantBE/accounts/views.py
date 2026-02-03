from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from restaurantBE.accounts.serializers import AccountSerializer, RegisterSerializer
from restaurantBE.utils.pagination.responses import apiError, apiSuccess


# Create your views here.
class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return apiSuccess(
                AccountSerializer(user).data,
                "register_success",
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            # Validation errors → 422
            return apiError(
                e.detail,
                "invalid_credentials",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            # Other errors → 400
            return apiError(
                str(e),
                "register_failed",
                status=status.HTTP_400_BAD_REQUEST,
            )
