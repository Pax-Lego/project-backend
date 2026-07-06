from django.contrib import admin

from apps.ingredients.models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_default",
        "calories_per_100g",
        "protein_g",
        "carbs_g",
        "fat_g",
        "user",
    ]
    list_filter = ["is_default", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
