from rest_framework.pagination import PageNumberPagination


class LimitUserPagination(PageNumberPagination):
    """Limit вместо значения по-умолчанию."""

    page_size_query_param = 'limit'
