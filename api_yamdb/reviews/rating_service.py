from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from reviews.models import Review


@receiver([post_save, post_delete], sender=Review)
def update_title_rating_on_review_change(sender, instance, **kwargs):
    """
    Обработчик сигналов для автоматического обновления рейтинга
    при создании, изменении или удалении отзывов.
    """

    title = instance.title

    avg_rating = Review.objects.filter(
        title=title
    ).aggregate(average_rating=Avg('score'))['average_rating']

    new_rating = round(avg_rating) if avg_rating is not None else None

    title.rating = new_rating
    title.save(update_fields=['rating'])
