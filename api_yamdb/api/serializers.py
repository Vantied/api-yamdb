from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Genre, Title


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


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создании названия произведения"""

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
        fields = ('name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        """Валидация года"""
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год не может быть больше текущего'
            )
        return value
