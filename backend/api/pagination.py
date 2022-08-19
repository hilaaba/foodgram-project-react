from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class LimitPageNumberPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
