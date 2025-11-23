from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from reviews.constants import (
    FORBIDDEN_USERNAMES, MAX_SCORE, MIN_SCORE, MIN_YEAR
)


def get_score_validators():
    """Возвращает общие валидаторы для оценки"""
    return [
        MinValueValidator(
            MIN_SCORE, f'Оценка не может быть меньше {MIN_SCORE}'),
        MaxValueValidator(
            MAX_SCORE, f'Оценка не может быть больше {MAX_SCORE}')
    ]


def validate_username_not_me(value):
    """Валидация имени пользователя."""
    if value.lower() == FORBIDDEN_USERNAMES:
        raise ValidationError('Использование имени "me" запрещено.')
    return value


username_validator = UnicodeUsernameValidator()


def get_year_validators():
    """Возвращает валидаторы для года."""
    current_year = timezone.now().year
    return [
        MinValueValidator(MIN_YEAR, f'Год не может быть меньше {MIN_YEAR}'),
        MaxValueValidator(current_year, 'Нельзя указывать год из будущего')
    ]
