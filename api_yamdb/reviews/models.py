from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.constants import (
    LAST_TWENTY_CHARS,
    NAME_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    SLUG_MAX_LENGTH,
)
from reviews.validators import (
    get_year_validators,
    get_score_validators,
    username_validator,
    validate_username_not_me
)


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
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator, validate_username_not_me]
    )
    email = models.EmailField(unique=True, max_length=EMAIL_MAX_LENGTH)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER
    )

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.username[:LAST_TWENTY_CHARS]

    @property
    def is_admin(self):
        return (self.role == self.Role.ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return (self.role == self.Role.MODERATOR
                or self.is_admin)


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
    year = models.SmallIntegerField(
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
    score = models.PositiveSmallIntegerField(validators=get_score_validators())

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
