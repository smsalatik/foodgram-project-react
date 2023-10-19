from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from constants import MAX_LENGHT, MAX_LENGHT_EMAIL


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )
    first_name = models.CharField(verbose_name='Имя', max_length=MAX_LENGHT)
    last_name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=MAX_LENGHT_EMAIL,
        verbose_name='email',
        unique=True)
    username = models.CharField(
        verbose_name='username',
        max_length=MAX_LENGHT,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """Модель Подписки."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',

    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id', )
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='author_user'
            )
        ]

    def __str__(self):
        return f'{self.author}-{self.user}'
