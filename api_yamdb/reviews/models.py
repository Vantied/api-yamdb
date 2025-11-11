from django.db import models


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


class Title(models.Model):
    '''Модель для произведений'''

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр'
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
