from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.reviews.constants import (
    CONFIRMATION_CODE_MAX_LENGTH, LAST_TWENTY_CHARS, ROLE_MAX_LENGTH
)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='email адрес',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль',
    )
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        blank=True,
        verbose_name='Код подтверждения',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username[:LAST_TWENTY_CHARS]

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_admin
from reviews.constants import (
    LAST_TWENTY_CHARS, MAX_LENGTH_NAME, MAX_LENGTH_SLUG
)


class Category(models.Model):
    '''Модель для категории'''

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]


class Genre(models.Model):
    '''Модель для жанра'''

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]


class Title(models.Model):
    '''Модель для произведений'''

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    year = models.IntegerField(
        verbose_name='Год выпуска'
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг на основе отзывов, если отзывов нет — `None`',
        null=True, blank=True
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]
