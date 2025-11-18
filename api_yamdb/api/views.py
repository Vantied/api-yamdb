import secrets

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import IsAdmin, IsAdminOrReadOnly
from api.serializers import (
    UserSerializer,
    UserMeSerializer,
    CategorySerializer,
    GenreSerializer,
    SignUpSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    TokenSerializer,
)
from reviews.models import Category, Genre, Title


User = get_user_model()


# ============================================================
#                    AUTHENTICATION
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    email = serializer.validated_data['email']

    user, _ = User.objects.get_or_create(username=username)

    if user.email != email:
        user.email = email

    user.confirmation_code = secrets.token_urlsafe(16)
    user.save(update_fields=['email', 'confirmation_code'])

    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        'noreply@example.com',
        [email],
    )

    return Response({'username': username, 'email': email})


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
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

    return Response({'token': str(AccessToken.for_user(user))})


# ============================================================
#                    COMMON BASE CLASSES
# ============================================================

class BaseSlugViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый ViewSet для моделей со slug и name. """

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class BaseFilteredModelViewSet(viewsets.ModelViewSet):
    """Базовый ViewSet для моделей с фильтрацией через DjangoFilterBackend."""

    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')


# ============================================================
#                    FILTERS
# ============================================================

class TitleFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter()

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')


# ============================================================
#                    USERS
# ============================================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            return Response(UserMeSerializer(user).data)

        serializer = UserMeSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ============================================================
#                    TITLES
# ============================================================

class TitleViewSet(BaseFilteredModelViewSet):
    queryset = Title.objects.all().select_related('category')
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateSerializer
        return TitleSerializer


# ============================================================
#                CATEGORY / GENRE
# ============================================================

class CategoryViewSet(BaseSlugViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseSlugViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
