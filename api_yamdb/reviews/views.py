from rest_framework import viewsets
from rest_framework.permissions import IsAuthorOrReadOnly

from reviews.models import Comment, Review
from reviews.serializers import CommentSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки операций CRUD с отзывами.

    Функции:
        - Создание нового отзыва
        - Получение списка всех отзывов
        - Получение детальной информации об отзыве
        - Обновление отзыва
        - Удаление отзыва

    Разрешения:
        - Аутентифицированные пользователи могут создавать отзывы
        - Только автор может изменять или удалять свой отзыв
        - Все пользователи могут просматривать отзывы
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для обработки операций CRUD с комментариями.

    Функции:
        - Создание нового комментария
        - Получение списка всех комментариев
        - Получение детальной информации о комментарии
        - Обновление комментария
        - Удаление комментария

    Разрешения:
        - Аутентифицированные пользователи могут создавать комментарии
        - Только автор может изменять или удалять свой комментарий
        - Все пользователи могут просматривать комментарии
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)
