from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ пользователей."""

    list_display = ('id', 'email', 'username', 'first_name',
                    'last_name')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ('id',)
    empty_value_display = '-пусто-'



@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ подписок."""

    list_display = ('user', 'author',)
    search_fields = ('user', 'author',)
    list_filter = ('user', 'author',)
    ordering = ('id',)
    empty_value_display = '-пусто-'
