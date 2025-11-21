from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from django.utils import timezone


def get_score_validators():
    """Возвращает общие валидаторы для оценки"""
    return [
        MinValueValidator(1, 'Оценка не может быть меньше 1'),
        MaxValueValidator(10, 'Оценка не может быть больше 10')
    ]


def validate_username_not_me(value):
    """Валидация: имя пользователя не может быть 'me'."""
    if value.lower() == 'me':
        raise ValidationError("Использование имени 'me' запрещено.")
    return value


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message="Недопустимые символы в username"
)


def get_year_validators():
    """Возвращает валидаторы для года."""
    current_year = timezone.now().year
    return [
        MinValueValidator(0, 'Год не может быть меньше 0'),
        MaxValueValidator(current_year, 'Нельзя указывать год из будущего')
    ]
