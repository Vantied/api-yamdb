from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import Category, Genre, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
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


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=(UniqueValidator(queryset=User.objects.all()),)
    )

    def validate_username(self, value):
        """Проверяет, что username не является зарезервированным именем."""

        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Использование имени 'me' в качестве username запрещено."
            )
        return value


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
