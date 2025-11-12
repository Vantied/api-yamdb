import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.serializers import (
    SignUpSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    TokenSerializer
)
from reviews.models import Title


User = get_user_model()


@api_view(['POST'])
def signup(request):
    """
    Эндпоинт регистрации нового пользователя.

    Принимает email и username, генерирует confirmation_code
    и отправляет его на email (в продакшене).

    Methods:
        POST: Создание нового пользователя или обновление кода подтверждения
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    username = serializer.validated_data['username']

    # Генерация кода подтверждения
    confirmation_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    # Создание или обновление пользователя
    user, created = User.objects.get_or_create(
        username=username,
        email=email,
        defaults={'confirmation_code': confirmation_code}
    )

    if not created:
        user.confirmation_code = confirmation_code
        user.save()

    send_mail(
        'Код подтверждения YaMDb',
        f'Ваш код подтверждения: {confirmation_code}',
        'yamdb@example.com',
        [email],
        fail_silently=False,
    )

    return Response(
        {'email': email, 'username': username},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
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
