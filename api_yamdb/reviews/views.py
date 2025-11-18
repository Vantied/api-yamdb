from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.permissions import IsModeratorOrAdminOrReadOnly
from reviews.models import Review, Title, Comment
from reviews.serializers import CommentSerializer, ReviewSerializer


# ---------------------------------------------------------
#                Общие миксины
# ---------------------------------------------------------

class ForbidPUTMixin:
    """Запрещает использование метода PUT во ViewSet."""

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(
                {"detail": "Метод PUT не разрешен"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class NestedModelViewSetMixin:
    """
    Общий функционал для вложенных ViewSet:
    - получение parent-объекта
    - фильтрация queryset по parent
    - автоматическое добавление parent при создании
    """

    parent_lookup_url_kwarg = 'title_id'
    parent_model = Title
    parent_field = 'title'

    def get_parent_object(self):
        """Получение родительского объекта через URL-параметр."""
        lookup_value = self.kwargs.get(self.parent_lookup_url_kwarg)
        return get_object_or_404(self.parent_model, pk=lookup_value)

    def get_queryset(self):
        """Фильтрация queryset по родительскому объекту."""
        parent = self.get_parent_object()
        return self.queryset.filter(**{self.parent_field: parent})

    def perform_create(self, serializer):
        """Создание записи с автоматическим указанием автора и parent."""
        parent = self.get_parent_object()
        serializer.save(author=self.request.user,
                        ** {self.parent_field: parent})


# ---------------------------------------------------------
#                      Review ViewSet
# ---------------------------------------------------------

class ReviewViewSet(ForbidPUTMixin,
                    NestedModelViewSetMixin,
                    viewsets.ModelViewSet):
    """
    CRUD для отзывов, связанных с конкретным произведением.
    URL:
        /api/v1/titles/<title_id>/reviews/
    """

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsModeratorOrAdminOrReadOnly,
    )

    queryset = Review.objects.all()

    parent_lookup_url_kwarg = "title_id"
    parent_model = Title
    parent_field = "title"


# ---------------------------------------------------------
#                     Comment ViewSet
# ---------------------------------------------------------

class CommentViewSet(ForbidPUTMixin,
                     NestedModelViewSetMixin,
                     viewsets.ModelViewSet):
    """
    CRUD для комментариев к отзывам.
    URL:
        /api/v1/titles/<title_id>/reviews/<review_id>/comments/
    """

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsModeratorOrAdminOrReadOnly,
    )

    queryset = Comment.objects.all()

    parent_lookup_url_kwarg = "review_id"
    parent_model = Review
    parent_field = "review"
