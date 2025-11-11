# Импорты для DRF будут раскомментированы после установки пакета
# from rest_framework import serializers
from reviews.models import Review, Comment


class CommentSerializer:
    """
    Сериализатор для модели Comment.

    Преобразования:
        - Объекты Comment в JSON
        - JSON в объекты Comment

    Поля:
        id: Уникальный идентификатор комментария
        text: Текст комментария
        author: Имя автора (только для чтения)
        pub_date: Дата публикации (только для чтения)


    Наследование от serializers.ModelSerializer будет добавлено
    после установки DRF
    """

    # Временная заглушка - будет заменена на serializers.ModelSerializer
    pass
