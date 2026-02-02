from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from restaurantBE.accounts.serializers import AccountSerializer, RegisterSerializer


# Create your views here.
class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {
                    "data": AccountSerializer(user).data,
                    "message": "Đăng ký thành công!",
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            # Validation errors → 422
            return Response(
                {"errors": e.detail},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            # Other errors → 400
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
