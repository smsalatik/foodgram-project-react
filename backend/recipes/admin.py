from django.contrib import admin

from .models import (ShoppingCart, Favorite, Ingredient, IngredientsInRecipe,
                     Recipe, Follow, Tag, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ пользователей."""

    list_display = ('id', 'email', 'username', 'first_name',
                    'last_name', 'password')
    search_fields = ('email', 'username', 'first_name',
                     'last_name', 'password')
    list_filter = ('email', 'username')


class RecipeIngredientAdmin(admin.StackedInline):
    """Передача ингредиентов в рецепты."""

    model = IngredientsInRecipe
    autocomplete_fields = ('ingredient',)
    min_num = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    """Админ рецептов."""

    list_display = ('id', 'author_name', 'name', 'text',
                    'cooking_time', 'recipes_tags', 'recipes_ingredients',
                    'favorite_count')
    list_filter = ('author', 'tags', 'name')
    search_fields = ('name', 'cooking_time', 'tags__name',
                     'author__email', 'ingredients__name')
    inlines = (RecipeIngredientAdmin,)

    @admin.display(description='отметок в избраном')
    def favorite_count(self, obj):
        """Отметоки в избраном у рецепта."""
        return obj.favorites.count()

    @admin.display(description='Автор')
    def author_name(self, obj):
        """Username автора рецепта."""
        return obj.author.username

    @admin.display(description='Теги')
    def recipes_tags(self, obj):
        """Теги рецепта."""
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингридиенты')
    def recipes_ingredients(self, obj):
        """Ингредиенты рецепта."""
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()])


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ корзины."""

    list_display = ('id', 'get_recipe', 'get_user',)
    search_fields = ('user__email', 'recipe__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    @admin.display(description='Имя рецепта')
    def get_recipe(self, obj):
        return obj.recipe.name

    @admin.display(description='Почта пользователя')
    def get_user(self, obj):
        return obj.user.email


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ Избранного."""

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ подписок."""

    list_display = ('id', 'author', 'user',
                    'email_user', 'email_author')
    search_fields = ('author', 'user')
    list_filter = ('author', 'user')

    @admin.display(description='Почта подписчика')
    def email_user(self, obj):
        """Почта подписчика."""
        return obj.user.email

    @admin.display(description='Почта автора')
    def email_author(self, obj):
        """Почта автора."""
        return obj.author.email


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Админка тэгов."""

    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('id', 'name', 'color', 'slug')
    list_filter = ('id', 'name', 'color', 'slug')
