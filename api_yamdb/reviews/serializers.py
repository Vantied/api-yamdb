from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Comment, Review, Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date', 'title')

    def validate(self, data):
        """
        Проверяет что пользователь не оставлял отзыв на это произведение.
        """
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            if title_id:
                title = get_object_or_404(Title, pk=title_id)
                author = self.context['request'].user

                if Review.objects.filter(title=title, author=author).exists():
                    raise serializers.ValidationError(
                        'Вы уже оставляли отзыв на это произведение'
                    )

        return data

    def validate_score(self, value):
        """Валидация оценки от 1 до 10"""
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10'
            )
        return value
