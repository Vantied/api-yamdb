from rest_framework import serializers
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
    """

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id',
                  'text',
                  'author',
                  'pub_date')
        read_only_fields = ('id',
                            'author',
                            'pub_date')


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
    """

    author = serializers.StringRelatedField(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id',
                  'title',
                  'text',
                  'author',
                  'score',
                  'pub_date',
                  'comments')
        read_only_fields = ('id',
                            'author',
                            'pub_date',
                            'comments')

    def validate_score(self, value):
        """
        Кастомная валидация для поля score.
        """
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10'
            )
        return value
