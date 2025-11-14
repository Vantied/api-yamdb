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


class Category(models.Model):
    '''Модель для категории'''

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
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
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
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
        max_length=NAME_MAX_LENGTH,
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


class Review(models.Model):
    """
    Модель для хранения отзывов пользователей на произведения.

    Атрибуты:
        title (ForeignKey): Ссылка на произведение, к которому написан отзыв
        text (TextField): Текст отзыва
        author (ForeignKey): Пользователь, оставивший отзыв
        score (IntegerField): Оценка произведения от 1 до 10
        pub_date (DateTimeField): Дата и время публикации отзыва
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть больше 10')
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:

        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Ограничение: один пользователь может оставить только один отзыв
        # на каждое произведение
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review'
            ),
        )

    def __str__(self):
        author_display = str(self.author)[:LAST_TWENTY_CHARS]
        title_display = str(self.title)[:LAST_TWENTY_CHARS]
        return f'Отзыв {author_display} на {title_display}'


class Comment(models.Model):
    """
    Модель для хранения комментариев пользователей к отзывам.

    Атрибуты:
        review (ForeignKey): Ссылка на отзыв, к которому оставлен комментарий
        text (TextField): Текст комментария
        author (ForeignKey): Пользователь, оставивший комментарий
        pub_date (DateTimeField): Дата и время публикации комментария
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:

        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        author_display = str(self.author)[:LAST_TWENTY_CHARS]
        return f'Комментарий {author_display} к отзыву {self.review.id}'
