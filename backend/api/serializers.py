from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from constants import MINIMUM_INGREDIENTS
from recipes.models import (ShoppingCart, Favorite, Ingredient,
                            IngredientsInRecipe,
                            Recipe, Follow, Tag, User)


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        """Получение значения подписки."""
        user = self.context.get('request').user
        return (user.is_authenticated
                and obj.following.filter(user=user).exists())

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'id')


class CustomUserCreateSerializer(UserCreateSerializer):
    """Переделаный из joser сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password', 'id')

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientsInRecipe.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class SubscribeUserSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = ('last_name', 'is_subscribed', 'id',
                  'username', 'email', 'first_name',
                  'recipes', 'recipes_count')
        read_only_fields = ('first_name', 'email', 'username', 'last_name')

    def get_recipes(self, data):
        """Получение рецептов автора."""
        recipes = data.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except Exception:
                pass
        serializer = BaseRecipeSerializer(recipes, many=True,
                                          read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientsInRecipeSerializer(
        read_only=True,
        many=True,
        source='ingredients_in_recipe',
    )

    def get_is_favorited(self, obj):
        """Добавлен ли рецепт избранное."""
        user = self.context.get('request').user
        return user.is_authenticated and user.favorites.filter(
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получаем значение, добавлен ли рецепт в корзину."""
        user = self.context.get('request').user
        return user.is_authenticated and user.shopping_cart.filter(
            recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')


class IngredientsinRecipeSerializerPost(serializers.ModelSerializer):
    """Сериализатор игредиентов при пост запросах."""

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class RecipesSerializerPost(serializers.ModelSerializer):
    """Сериализатор при пост запросах."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsinRecipeSerializerPost(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'id',
                  'name', 'text', 'cooking_time', 'author')

    def validate(self, data):
        """Валидация данных."""
        list_of_ingredients = []
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError('Нет ингредиентов, '
                                              'не из чего готовить!')
        for ingredient in ingredients:

            value = get_object_or_404(Ingredient, id=ingredient['id'])
            if ingredient['amount'] < MINIMUM_INGREDIENTS:
                raise ValidationError('не правильное значение')
            if value in list_of_ingredients:
                raise ValidationError('Ингредиенты не должны повторяться')
            list_of_ingredients.append(value)

        tags = self.initial_data.get('tags')
        list_of_tags = []
        if not tags:
            raise ValidationError('Ингредиент не заполнено')
        for tag in tags:
            if tag in list_of_tags:
                raise ValidationError('Тег не должен повторяться')
            list_of_tags.append(tag)

        return data

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Нет картинки')
        return image

    def cooking_ingredients(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            ingredient_all = IngredientsInRecipe(
                ingredient_id=ingredient_data.get('id'),
                recipe=recipe,
                amount=amount
            )
            recipe_ingredients.append(ingredient_all)
        IngredientsInRecipe.objects.bulk_create(recipe_ingredients)

    def update(self, instance, validated_data):
        """Обновление пецепта."""
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self.cooking_ingredients(ingredients, instance)
        instance.save()
        return instance

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.cooking_ingredients(ingredients, recipe)

        return recipe

    def to_representation(self, instance):
        """Возвращение рецепта."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance,
                                context=context).data


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в корзину."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializerPost(serializers.ModelSerializer):
    """Сериализатор пост подписки."""

    class Meta:
        model = Follow
        fields = ('author', 'user')

    def validate(self, data):
        author = data.get('author')
        user = data.get('user')
        if user.follower.filter(author=author).exists():
            raise ValidationError(
                detail='Нельзя подписаться второй раз',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def to_representation(self, instance):
        return SubscribeUserSerializer(
            instance.author, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избраного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        if self.Meta.model.objects.filter(user=data['user'],
                                          recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Нельзядважды добавить рецепт.')
        return data

    def to_representation(self, instance):
        return BaseRecipeSerializer(
            instance.recipe,
            context=self.context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор для карзины."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
