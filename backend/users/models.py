from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'

ACCESS_LEVELS = (
    (USER, 'Авторизованный пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    """
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    access_level = models.CharField(
        max_length=150,
        choices=ACCESS_LEVELS,
        blank=True,
        default='user',
        verbose_name='Уровень доступа'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_superuser or self.access_level == 'admin'


class Follow(models.Model):
    """
    Модель подписок
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        models.UniqueConstraint(
            fields=('user', 'author'),
            name='unique follow',
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        default_related_name = 'follows'

    def __str__(self):
        return (
            f'user: {self.user.username}, '
            f'author: {self.author.username}'
        )


