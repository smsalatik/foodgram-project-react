from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class FilterRecipes(FilterSet):
    """Фильтер для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             to_field_name='slug',
                                             field_name='tags__slug')

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр для покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр для избранного."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class FilterSearchForName(FilterSet):
    """Фильтр name."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
