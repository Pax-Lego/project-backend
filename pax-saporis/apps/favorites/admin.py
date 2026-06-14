from django.contrib import admin
from apps.favorites.models import FavoriteIngredient, FavoriteRecipe, FavoritePlan


@admin.register(FavoriteIngredient)
class FavoriteIngredientAdmin(admin.ModelAdmin):
    list_display = ['user', 'ingredient', 'created_at']
    search_fields = ['user__email', 'ingredient__name']


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']
    search_fields = ['user__email', 'recipe__name']


@admin.register(FavoritePlan)
class FavoritePlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'created_at']
    search_fields = ['user__email', 'plan__name']