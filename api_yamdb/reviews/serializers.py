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


class ReviewSerializer:
    """
    Сериализатор для модели Review.

    Преобразования:
        - Объекты Review в JSON
        - JSON в объекты Review

    Поля:
        id: Уникальный идентификатор отзыва
        title: Произведение, к которому оставлен отзыв
        text: Текст отзыва
        author: Имя автора (только для чтения)
        score: Оценка произведения
        pub_date: Дата публикации (только для чтения)
        comments: Список комментариев к отзыву (только для чтения)


    Наследование от serializers.ModelSerializer будет добавлено
    после установки DRF
    """

    # Временная заглушка - будет заменена на serializers.ModelSerializer
    pass
