from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    page_size = settings.PAGINATION_PAGE_SIZE
