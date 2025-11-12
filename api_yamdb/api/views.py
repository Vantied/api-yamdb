from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from api.serializers import TitleCreateSerializer, TitleSerializer
from reviews.models import Title


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
