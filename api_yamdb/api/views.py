from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAdmin
from api.serializers import (
    TitleCreateSerializer, TitleSerializer, UserMeSerializer, UserSerializer
)
from reviews.models import Title


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserMeSerializer(request.user)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = UserMeSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class TitleFilter(django_filters.FilterSet):
    """
    Кастомный фильтр для произведений.
    Соответствует параметрам из API документации:
    category: фильтрует по slug категории
    genre: фильтрует по slug жанра
    name: поиск по названию (регистронезависимый)
    year: фильтрует по году выпуска
    """
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с произведениями.
    Предоставляет полный CRUD для произведений:
    list: получение списка произведений с фильтрацией
    retrieve: получение конкретного произведения
    create: добавление нового произведения (только для администраторов)
    update/partial_update: изменение произведения (только для администраторов)
    destroy: удаление произведения (только для администраторов)
    Фильтрация осуществляется через параметры:
    ?category=films - по категории
    ?genre=action - по жанру
    ?name=matrix - по названию
    ?year=2020 - по году выпуска
    """
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer
