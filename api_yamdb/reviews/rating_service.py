from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from reviews.models import Review


class RatingService:
    """
    Сервис для расчета и обновления рейтингов произведений.
    """

    @staticmethod
    def calculate_title_rating(title):
        """
        Рассчитывает рейтинг произведения на основе отзывов.
        """
        avg_rating = Review.objects.filter(
            title=title
        ).aggregate(average_rating=Avg('score'))['average_rating']

        return round(avg_rating) if avg_rating is not None else None

    @staticmethod
    def update_title_rating(title):
        """
        Обновляет рейтинг произведения в базе данных.
        """
        new_rating = RatingService.calculate_title_rating(title)
        title.rating = new_rating
        title.save(update_fields=['rating'])
        return new_rating


@receiver([post_save, post_delete], sender=Review)
def update_title_rating_on_review_change(sender, instance, **kwargs):
    """
    Обработчик сигналов для автоматического обновления рейтинга
    при создании, изменении или удалении отзывов.
    """
    RatingService.update_title_rating(instance.title)
