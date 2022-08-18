import re

from django.core.exceptions import ValidationError

MAX_LENGTH = 150


def validate_user(value):
    """
    Проверка поля username модели user.
    """
    if value == 'me':
        raise ValidationError(
            f'Использовать имя {value} в качестве username запрещено.'
        )
    if re.search(r'[^\w.@+-]', value) or len(value) > MAX_LENGTH:
        raise ValidationError(
            'Required. 150 characters or fewer.'
            'Letters, digits and @/./+/-/_ only.'
        )
