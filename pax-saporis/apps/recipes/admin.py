from django.contrib import admin

from apps.recipes.models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_default",
        "user",
        "total_calories",
        "total_protein",
        "total_carbs",
        "total_fat",
        "created_at",
    ]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name"]
    readonly_fields = [
        "total_calories",
        "total_protein",
        "total_carbs",
        "total_fat",
        "created_at",
        "updated_at",
    ]
    inlines = [RecipeIngredientInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = [
        "recipe",
        "ingredient",
        "quantity_g",
        "calories",
        "protein",
        "carbs",
        "fat",
        "created_at",
    ]
    search_fields = ["recipe__name", "ingredient__name"]
    readonly_fields = ["calories", "protein", "carbs", "fat", "created_at"]
