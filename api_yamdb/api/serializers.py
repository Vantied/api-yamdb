from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator

from api.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import (
    get_score_validators,
    username_validator,
    validate_username_not_me,
)

User = get_user_model()


# ============================================================
#                    BASE SERIALIZERS
# ============================================================

class BaseNameSlugSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для моделей с полями name/slug."""

    rating = serializers.IntegerField(read_only=True)

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

    rating = serializers.IntegerField(read_only=True)

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


# ============================================================
#                    SIGNUP & TOKEN
# ============================================================

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True
    )
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
        validators=[username_validator, validate_username_not_me]
    )

    def validate(self, data):
        username = data['username']
        email = data['email']

        if User.objects.filter(username=username).exclude(
            email=email
        ).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )

        if User.objects.filter(email=email).exclude(
            username=username
        ).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

        return data

    def create(self, validated_data):
        """Создаёт или обновляет пользователя."""
        username = validated_data['username']
        email = validated_data['email']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created and user.email != email:
            user.email = email
            user.save(update_fields=['email'])

        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[username_validator, validate_username_not_me]
    )
    confirmation_code = serializers.CharField()

    def validate_username(self, value):
        """Проверяем существование пользователя."""
        if not User.objects.filter(username=value).exists():
            raise NotFound('Пользователь не найден')
        return value

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        user = User.objects.get(username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )

        data['user'] = user
        return data


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


# ============================================================
#                      REVIEW / COMMENT
# ============================================================

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date', 'title')

    def validate(self, data):
        """
        Проверяет что пользователь не оставлял отзыв на это произведение.
        """
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            if title_id:
                title = get_object_or_404(Title, pk=title_id)
                author = self.context['request'].user

                if Review.objects.filter(title=title, author=author).exists():
                    raise serializers.ValidationError(
                        'Вы уже оставляли отзыв на это произведение'
                    )

        return data

    def validate_score(self, value):
        """Валидация оценки от 1 до 10 с использованием общих правил"""

        validators = get_score_validators()
        for validator in validators:
            validator(value)
        return value
