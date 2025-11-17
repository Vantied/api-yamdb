from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import IsModeratorOrAdminOrReadOnly
from reviews.models import Review, Title
from reviews.serializers import CommentSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsModeratorOrAdminOrReadOnly
    )

    def get_title(self):
        """Получает title по title_id из URL"""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает отзывы для конкретного title"""
        title = self.get_title()
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        """Создает отзыв с автором и title"""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT-запросы"""
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод PUT не разрешен'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsModeratorOrAdminOrReadOnly
    )

    def get_review(self):
        """Получает review по review_id из URL"""
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Возвращает комментарии для конкретного отзыва"""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Создает комментарий с автором и review"""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        """Запрещаем PUT-запросы"""
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод PUT не разрешен'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)
