from rest_framework.pagination import PageNumberPagination


from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound
from django.utils.translation import gettext_lazy as _


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 50
    page_query_param = "page"

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except NotFound:
            raise ValidationError({"page": _("invalid_page_number")})
