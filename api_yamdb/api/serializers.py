from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import Category, Genre, Title

User = get_user_model()


# ============================================================
#                    BASE SERIALIZERS
# ============================================================

class BaseNameSlugSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для моделей с полями name/slug."""

    class Meta:
        fields = ('name', 'slug')
        read_only_fields = ('id',)
        abstract = True


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для отображения данных пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        abstract = True


class BaseTitleSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для Title — общие поля."""

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description',
            'genre', 'category', 'rating'
        )
        read_only_fields = ('id', 'rating')
        abstract = True


# ============================================================
#                    USERS
# ============================================================

class UserSerializer(BaseUserSerializer):
    """Полный CRUD пользователя (для админов)."""

    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )


class UserMeSerializer(BaseUserSerializer):
    """Профиль текущего пользователя. Роль менять нельзя."""

    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ('role',)


# ============================================================
#                    SIGNUP & TOKEN
# ============================================================

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message="Недопустимые символы в username"
            )
        ]
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Использование имени 'me' запрещено."
            )
        return value

    def validate(self, data):
        username = data['username']
        email = data['email']

        # username занят другим email
        if User.objects.filter(username=username).exclude(
            email=email
        ).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )

        # email занят другим username
        if User.objects.filter(email=email).exclude(
            username=username
        ).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

        return data

    def create(self, validated_data):
        """Создаёт пользователя и обновляет email при несовпадении."""
        username = validated_data['username']
        email = validated_data['email']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created and user.email != email:
            user.email = email

        # Генерация нового confirmation_code
        user.confirmation_code = get_random_string(length=24)
        user.save(update_fields=['email', 'confirmation_code'])

        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()


# ============================================================
#                    CATEGORY / GENRE
# ============================================================

class CategorySerializer(BaseNameSlugSerializer):
    class Meta(BaseNameSlugSerializer.Meta):
        model = Category


class GenreSerializer(BaseNameSlugSerializer):
    class Meta(BaseNameSlugSerializer.Meta):
        model = Genre


# ============================================================
#                      TITLES
# ============================================================

class TitleSerializer(BaseTitleSerializer):
    """Чтение произведения — вложенные жанры и категории."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)


class TitleCreateSerializer(BaseTitleSerializer):
    """Создание/обновление произведения — slug поля."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta(BaseTitleSerializer.Meta):
        read_only_fields = ('id', 'rating')

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего.'
            )
        return value
