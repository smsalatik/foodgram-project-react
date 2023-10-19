from django.core.exceptions import ValidationError


def more_one(value):
    """Проверка времени приготовления."""
    if value < 1:
        raise ValidationError('Временя приготовления не может '
                              'быть меньше или равно 0')
