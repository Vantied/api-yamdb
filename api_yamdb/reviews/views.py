from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from reviews.models import Comment, Review, Title
from reviews.serializers import CommentSerializer, ReviewSerializer
from api.permissions import IsOwnerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        # Проверяем существование Title *после* валидации данных
        # Это может вызвать 404, но это корректное поведение
        # если title_id не существует в URL
        title = get_object_or_404(Title, pk=title_id)

        author = self.request.user

        # Проверяем уникальность перед сохранением
        if Review.objects.filter(title=title, author=author).exists():
            raise ValidationError('Вы уже оставляли отзыв на это произведение')

        serializer.save(author=author, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)