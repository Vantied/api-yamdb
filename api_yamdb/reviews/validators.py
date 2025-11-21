from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


def get_score_validators():
    """Возвращает общие валидаторы для оценки"""
    return [
        MinValueValidator(1, 'Оценка не может быть меньше 1'),
        MaxValueValidator(10, 'Оценка не может быть больше 10')
    ]


def get_year_validators():
    """Возвращает валидаторы для года."""
    current_year = timezone.now().year
    return [
        MinValueValidator(0, 'Год не может быть меньше 0'),
        MaxValueValidator(current_year, 'Нельзя указывать год из будущего')
    ]
