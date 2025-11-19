# reviews/validators.py
from django.core.validators import MinValueValidator, MaxValueValidator


def get_score_validators():
    """Возвращает общие валидаторы для оценки"""
    return [
        MinValueValidator(1, 'Оценка не может быть меньше 1'),
        MaxValueValidator(10, 'Оценка не может быть больше 10')
    ]
