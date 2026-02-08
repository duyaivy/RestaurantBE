from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100
    min_limit = 1
    min_offset = 0
    max_offset = 50
    limit_query_param = "limit"
    offset_query_param = "offset"
