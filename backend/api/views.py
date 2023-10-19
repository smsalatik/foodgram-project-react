from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (ShoppingCart, Favorite, Ingredient,
                            IngredientsInRecipe,
                            Recipe, Follow, Tag, User)
from .filters import FilterSearchForName, FilterRecipes
from .pagination import LimitUserPagination
from .permission import AuthorOrReadOnly
from .serializers import (ShoppingCartSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipesSerializerPost, FollowSerializerPost,
                          RecipeSerializer, SubscribeUserSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    """Вью юсеров."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitUserPagination
    permission_classes = (AuthorOrReadOnly,)

    def get_permissions(self):
        """Выбор пермишена."""
        if self.action == 'create':
            return [AllowAny(), ]
        if self.action == 'me':
            return [IsAuthenticated(), ]
        return [AuthorOrReadOnly(), ]

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def subscribe(self, request, id):
        """Подписка."""
        get_object_or_404(User, id=id)
        if request.method == 'POST':
            user = request.user
            data = {'user': user.id, 'author': id}
            serializer = FollowSerializerPost(data=data,
                                              context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        data = Follow.objects.filter(user_id=request.user.id,
                                     author_id=id)
        if request.method == 'DELETE':
            if data.exists():
                data.delete()
                return Response({'Отлично': 'Вы отписаны от автора'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'Ошибка': 'Неправильные данные'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            permission_classes=(IsAuthenticated,),
            detail=False, )
    def subscriptions(self, request):
        """Все подписки пользователя."""
        page = self.paginate_queryset(User.objects.filter(
            following__user=request.user))
        serializer = SubscribeUserSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вью тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewsSet(viewsets.ReadOnlyModelViewSet):
    """Вью ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('^name',)
    filterset_class = FilterSearchForName


class RecipeViewsSet(ModelViewSet):
    """Вью рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterRecipes
    pagination_class = LimitUserPagination

    def get_serializer_class(self):
        """Выбор серилизатора."""
        if self.request.method == 'PATCH' or self.request.method == 'POST':
            return RecipesSerializerPost
        return RecipeSerializer

    def perform_create(self, serializer):
        """Создание рецепта."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Изменение созданного рецепта."""
        serializer.save(author=self.request.user)

    @staticmethod
    def favorite_shoppingcart_funk(serializer, request, pk):
        """Дублирующийся код в избранном и корзине."""
        data = {'user': request.user.id, 'recipe': pk}
        context = {'request': request}
        serializer = serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True)
    def favorite(self, request, pk):
        """Добавление/удаление избранных рецептов."""
        if request.method == 'POST':
            return self.favorite_shoppingcart_funk(
                FavoriteSerializer, request, pk)
        if request.method == "DELETE":
            data = Favorite.objects.filter(user=request.user, recipe__id=pk)
            if data.exists():
                data.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        get_object_or_404(Recipe, id=pk)
        return Response({'ошибка': 'Нет такого рецепта'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            detail=True,
            )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину."""
        if request.method == 'POST':
            return self.favorite_shoppingcart_funk(
                ShoppingCartSerializer, request, pk)
        if request.method == 'DELETE':
            data = ShoppingCart.objects.filter(
                user_id=request.user.id, recipe_id=pk)
            if data.exists():
                data.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        get_object_or_404(Recipe, id=pk)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            permission_classes=[IsAuthenticated],
            detail=False)
    def download_shopping_cart(self, request):
        """Скачивание рецепта."""
        if request.user.shopping_cart.exists():
            ingredients_recipe = IngredientsInRecipe.objects.filter(
                recipe__shopping_cart__user=request.user)
            values = ingredients_recipe.values('ingredient__name',
                                               'ingredient__measurement_unit')
            ingredients = values.annotate(amount=Sum('amount'))

            shop_cart = 'Список покупок.\n'
            for ingredient in ingredients:
                shop_cart += (f'{ingredient["ingredient__name"]} - '
                              f'{ingredient["ingredient__measurement_unit"]} '
                              f'({ingredient["amount"]})\n')

            filename = 'Покупоки.txt'
            response = HttpResponse(shop_cart,
                                    content_type='text/plain')
            response['Content-Disposition'] = (f'attachment; '
                                               f'filename={filename}')
            return response
        return Response(status=status.HTTP_400_BAD_REQUEST)
