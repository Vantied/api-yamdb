from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from reviews.models import Comment, Review, Title
from reviews.serializers import CommentSerializer, ReviewSerializer
from api.permissions import IsOwnerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки операций CRUD с отзывами.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        """
        Возвращает queryset отзывов для конкретного произведения.
        """
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def get_title(self):
        """
        Получает объект произведения или возвращает 404.
        """
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def list(self, request, *args, **kwargs):
        """
        Получение списка всех отзывов для произведения.
        """
        self.get_title()

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Автоматически устанавливает автора отзыва и произведение при создании.
        """
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки операций CRUD с комментариями.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        """
        Возвращает queryset комментариев для конкретного отзыва.
        """
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def get_review(self):
        """
        Получает объект отзыва или возвращает 404.
        """
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        get_object_or_404(Title, id=title_id)

        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review

    def perform_create(self, serializer):
        """
        Автоматически устанавливает автора комментария и отзыв при создании.
        """
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
