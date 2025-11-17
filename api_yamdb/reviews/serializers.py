from rest_framework import serializers

from reviews.models import Comment, Review, Title # <-- Добавлен импорт Title


class CommentSerializer(serializers.ModelSerializer):
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


class ReviewSerializer(serializers.ModelSerializer):
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

    def get_comments(self, obj):
        """Получает все комментарии для отзыва."""
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

    def validate(self, data):
        """
        Проверяет что пользователь не оставлял отзыв на это произведение.

        Args:
            data: Валидируемые данные

        Returns:
            dict: Проверенные данные

        Raises:
            ValidationError: Если пользователь уже оставлял отзыв
        """
        if self.context['request'].method == 'POST':
            # title_id из URL, получаем из view
            try:
                title_id = self.context['view'].kwargs['title_id']
                title = Title.objects.get(pk=title_id)
            except KeyError:
                # если title_id нет в kwargs, значит, вызов не из ReviewViewSet
                title = data.get('title')
            except Title.DoesNotExist:
                title = None

            author = self.context['request'].user

            if title and author:
                if Review.objects.filter(title=title, author=author).exists():
                    raise serializers.ValidationError(
                        'Вы уже оставляли отзыв на это произведение'
                    )

        return data

    def validate_score(self, value):
        """
        Кастомная валидация для поля score.

        Args:
            value: Значение оценки

        Returns:
            int: Проверенное значение оценки

        Raises:
            ValidationError: Если оценка не в диапазоне 1-10
        """
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10'
            )
        return value