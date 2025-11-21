from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (
    CONFIRMATION_CODE_MAX_LENGTH,
    LAST_TWENTY_CHARS,
    NAME_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    SLUG_MAX_LENGTH
)
from reviews.validators import get_score_validators, get_year_validators


# --------------------------------------
#  Базовые абстрактные классы
# --------------------------------------

class BaseNamedSlugModel(models.Model):
    """Базовая модель с полями name + slug"""

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]


class BaseTextAuthorDateModel(models.Model):
    """Базовая модель для сущностей с текстом, автором и датой публикации"""

    text = models.TextField()
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# --------------------------------------
# Пользователь
# --------------------------------------

class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField(unique=True, max_length=254)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=ROLE_MAX_LENGTH,
                            choices=ROLE_CHOICES, default=USER)
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH, blank=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.username[:LAST_TWENTY_CHARS]

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_admin


# --------------------------------------
# Категории и жанры
# --------------------------------------

class Category(BaseNamedSlugModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNamedSlugModel):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


# --------------------------------------
# Title
# --------------------------------------

class Title(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='titles')
    genre = models.ManyToManyField(Genre, related_name='titles')
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    year = models.PositiveSmallIntegerField(
        validators=get_year_validators()
    )
    description = models.TextField()

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]


# --------------------------------------
# Review
# --------------------------------------

class Review(BaseTextAuthorDateModel):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(validators=get_score_validators())

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'),
        )

    def __str__(self):
        return (
            f'Отзыв {self.author.username[:LAST_TWENTY_CHARS]} на '
            f'{self.title.name[:LAST_TWENTY_CHARS]}'
        )


# --------------------------------------
# Comment
# --------------------------------------

class Comment(BaseTextAuthorDateModel):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f'Комментарий {self.author.username[:LAST_TWENTY_CHARS]} '
            f'к отзыву {self.review.id}'
        )
