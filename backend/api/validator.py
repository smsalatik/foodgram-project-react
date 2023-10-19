from django.core.exceptions import ValidationError

from constants import MIN_TIME, MAX_TIME


def cooking_time_validator(value):
    """Времени приготовления."""
    try:
        if value <= MIN_TIME or value >= MAX_TIME:
            raise ValidationError('Неверно указано время')
    except ValueError:
        raise ValidationError('Неверный тип данных')
