from rest_framework.permissions import IsAuthenticated
from restaurantBE.utils.responses import apiError, apiSuccess
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.utils.translation import gettext as _
from restaurantBE.constants.common import Constant
import cloudinary.uploader


class UploadImageView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    # Không cần authentication_classes - dùng JWTAuthentication mặc định từ settings.py
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return apiError(None, _("no_file_provided"), status=status.HTTP_400_BAD_REQUEST)
        if file.size > Constant.MAX_FILE_SIZE:
            return apiError(None, _("file_too_large"), status=status.HTTP_400_BAD_REQUEST)
        if file.content_type not in Constant.ALLOWED_IMAGE_FORMATS:
            return apiError(None, _("file_type_not_allowed"), status=status.HTTP_400_BAD_REQUEST)
        
        result = cloudinary.uploader.upload(
            file,
            folder="uploads",
            resource_type="auto"  
        )
        image_url = result.get('secure_url') or result.get('url')
        return apiSuccess(image_url, _("file_uploaded_successfully"), status=status.HTTP_201_CREATED)