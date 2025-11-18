from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        """
        Запускается при готовности приложения.
        Подключает обработчики для автоматического обновления рейтингов.
        """
        from reviews import rating_service
        _ = rating_service
