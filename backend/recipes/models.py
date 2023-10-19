from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validator import cooking_time_validator
from constants import MAX_COLOR, MAX_LENGHT, MAX_LENGHT_TEXT

from .validator import more_one


class User(AbstractUser):
    """Модель пользователя."""

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    email = models.EmailField(
        verbose_name='Почта',
        unique=True,
        max_length=MAX_LENGHT,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """Модель Подписки."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='following'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',

    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'],
            name='author_user')]

    def __str__(self):
        return f'{self.author}-{self.user}'


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(
        max_length=MAX_LENGHT,
        unique=True,
        null=False,
        verbose_name='Имя',
        blank=False,
    )
    color = ColorField(
        max_length=MAX_COLOR,
        blank=False,
        null=False,
        verbose_name='Цвет',
        db_index=True,
        unique=True,
        format='hex',
        default='#999999',
    )
    slug = models.SlugField(
        max_length=MAX_LENGHT,
        verbose_name='слаг',
        blank=False,
        unique=True,
        null=False,

    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель Ингредиента."""

    name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Название ингридиента',

    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(fields=['name',
                                                       'measurement_unit'],
                                               name='name_measurement_unit')]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель Рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Изображение Блюда',
        upload_to='recipes/',
        blank=False,
    )
    name = models.CharField(
        max_length=MAX_LENGHT,
        verbose_name='Название блюда',
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
        max_length=MAX_LENGHT_TEXT
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(cooking_time_validator, )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientsInRecipe',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.name}'


class IngredientsInRecipe(models.Model):
    """Модель ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe',
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[more_one]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                               name='ingredient_recipe')]

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Избранный пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Рецепты избранного пользователя',
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_favorite_recipe')]

    def __str__(self):
        return f'{self.user}-{self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзины покупателя."""

    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Владелец корзины',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Рецепты в корзине',
    )

    class Meta:
        verbose_name = 'Покупка в корзине'
        verbose_name_plural = 'Покупки в корзине'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart_recipe')]

    def __str__(self):
        return f'{self.user}-{self.recipe}'
