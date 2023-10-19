from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'
router = DefaultRouter()

router.register('users',
                views.CustomUserViewSet, basename='users')
router.register('tags',
                views.TagViewSet, basename='tags')
router.register('recipes',
                views.RecipeViewsSet, basename='recipes')
router.register('ingredients',
                views.IngredientsViewsSet, basename='ingredients')
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
