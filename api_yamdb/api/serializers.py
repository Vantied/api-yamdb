from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string

from api.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import Category, Genre, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


# api/serializers.py

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        # Убираем UniqueValidator, будем проверять в create
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        # Убираем UniqueValidator, будем проверять в create
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы в username'
            )
        ]
    )

    def validate_username(self, value):
        """Проверяет, что username не является зарезервированным именем."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Использование имени 'me' в качестве username запрещено."
            )
        return value

    def validate(self, data):
        """Проверяет уникальность username и email."""
        username = data.get('username')
        email = data.get('email')

        # Проверяем, существует ли пользователь с таким username
        if User.objects.filter(username=username).exclude(email=email).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )

        # Проверяем, существует ли пользователь с таким email
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

        return data

    def create(self, validated_data):
        """
        Создает пользователя или возвращает существующего.
        Генерирует confirmation_code для проверки email.
        """
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )

        # Если пользователь уже существует, обновляем email (если нужно)
        if not created and user.email != validated_data['email']:
            user.email = validated_data['email']
            user.save(update_fields=['email'])

        # Генерируем confirmation_code
        user.confirmation_code = get_random_string(length=24)
        user.save(update_fields=['confirmation_code'])

        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH
    )
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории"""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        read_only_fields = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        read_only_fields = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для чтение названия произведения"""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
        read_only_fields = ('id',)


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведений"""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating',
        )
        read_only_fields = ('id', 'rating')

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего'
            )
        return value
