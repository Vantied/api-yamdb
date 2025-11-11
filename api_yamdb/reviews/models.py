from django.db import models

from reviews.constants import LAST_TWENTY_CHARS


class Category(models.Model):
    '''Модель для категории'''

    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]


class Genre(models.Model):
    '''Модель для жанра'''

    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

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
        max_length=256,
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

    def __str__(self):
        return self.name[:LAST_TWENTY_CHARS]
