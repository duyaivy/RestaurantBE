from django.urls import path
from .views import UploadImageView

urlpatterns = [
    path("media/upload/", UploadImageView.as_view()),
]
