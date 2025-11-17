from rest_framework import viewsets

from reviews.models import Comment, Review
from reviews.serializers import CommentSerializer, ReviewSerializer
from api.permissions import IsOwnerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с отзывами.

    Предоставляет полный CRUD для отзывов:
    - list: получение списка отзывов (доступно без токена)
    - retrieve: получение конкретного отзыва (доступно без токена)
    - create: создание отзыва (только аутентифицированные пользователи)
    - update/partial_update: изменение отзыва
    - destroy: удаление отзыва (только автор, модератор или администратор)

    Ограничения:
    - Один пользователь может оставить только один отзыв на произведение
    - Оценка должна быть в диапазоне от 1 до 10
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        """Автоматически устанавливает автора отзыва при создании."""
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с комментариями.

    Предоставляет полный CRUD для комментариев:
    - list: получение списка комментариев (доступно без токена)
    - retrieve: получение конкретного комментария (доступно без токена)
    - create: создание комментария (только аутентифицированные пользователи)
    - update/partial_update: изменение комментария
    - destroy: удаление комментария (только автор, модератор или администратор)
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        """Автоматически устанавливает автора комментария при создании."""
        serializer.save(author=self.request.user)
