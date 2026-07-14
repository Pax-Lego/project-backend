from django.contrib import admin

from apps.lists.models import IngredientList, RecipeList


@admin.register(IngredientList)
class IngredientListAdmin(admin.ModelAdmin):
    list_display = ["name", "is_builtin", "user"]
    list_filter = ["is_builtin"]
    search_fields = ["name", "user__email"]


@admin.register(RecipeList)
class RecipeListAdmin(admin.ModelAdmin):
    list_display = ["name", "is_builtin", "user"]
    list_filter = ["is_builtin"]
    search_fields = ["name", "user__email"]
