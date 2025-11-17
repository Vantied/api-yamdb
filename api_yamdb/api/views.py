import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny

from api.permissions import IsAdmin, IsAdminOrReadOnly
from api.serializers import (
    UserSerializer,
    UserMeSerializer,
    CategorySerializer,
    GenreSerializer,
    SignUpSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    TokenSerializer
)
from reviews.models import Category, Genre, Title


User = get_user_model()



@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    email = serializer.validated_data['email']

    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )

    # Обновляем email, если он изменился
    if not created and user.email != email:
        user.email = email
        user.save(update_fields=['email'])

    # Обновляем confirmation_code
    user.confirmation_code = secrets.token_urlsafe(16)
    user.save(update_fields=['confirmation_code'])

    # Отправка письма с кодом подтверждения
    send_mail(
        'Код подтверждения',
        f'Ваш код: {user.confirmation_code}',
        'from@example.com',
        [email],
    )

    return Response({'email': email, 'username': username}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """
    Эндпоинт получения JWT токена.

    Принимает username и confirmation_code, возвращает access token.

    Methods:
        POST: Получение JWT токена после подтверждения email
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']

    user = get_object_or_404(User, username=username)

    if user.confirmation_code != confirmation_code:
        return Response(
            {'confirmation_code': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )

    token = AccessToken.for_user(user)

    return Response({'token': str(token)}, status=status.HTTP_200_OK)


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)  # <-- Добавлено
    search_fields = ('username',)      # <-- Добавлено

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
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
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    Вьюсет для работы с категориями.
    Предоставляет операции:
    - list: получение списка категорий (доступно без токена)
    - create: создание категории (только для администраторов)
    - destroy: удаление категории (только для администраторов)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    Вьюсет для жанров.

    Доступ:
    - GET /api/v1/genres/ — список всех жанров (доступно без токена)
    - POST /api/v1/genres/ — создать жанр (только администратор)
    - DELETE /api/v1/genres/{slug}/ — удалить жанр (только администратор)
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'