from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
        'titles.Title',  # Ссылка на модель произведений (позже)
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        'users.User',  # Ссылка на модель пользователей (позже)
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
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв {self.author} на {self.title}'
